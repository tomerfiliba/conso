import os
import sys
import re
import time
import termios
import codecs
import select
import curses
import locale
import signal
import errno


termios.IFLAG = 0
termios.OFLAG = 1
termios.CFLAG = 2
termios.LFLAG = 3
termios.ISPEED = 4
termios.OSPEED = 5
termios.CC = 6


class CursorInfo(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self._x = 0
        self._y = 0
        self._visible = True
    def _set(self, x, y):
        self._x = x
        self._y = y
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @property
    def visible(self):
        return self._visible

    def move(self, x, y):
        self.terminal._write(curses.tparm(self.terminal._CURSOR_ADDRESS_template, y, x))
    def hide(self):
        self.terminal._write(self.terminal._CURSOR_HIDE)
        self._visible = False
    def show(self):
        self.terminal._write(self.terminal._CURSOR_SHOW)
        self._visible = True
    
    def _resized(self, width, height):
        self._x = min(self._x, width)
        self._y = min(self._y, height)
    
    def write(self, text, pos = None):
        if pos is not None:
            x, y = pos
            self.move(x, y)
        self.terminal._write(text)
        offset = self._x + len(text)
        self._x = offset % self.terminal._width
        self._y = max(self._y + offset // self.terminal._width, self.terminal._height - 1)

class Event(object):
    __slots__ = ["value"]
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class Char(Event):
    __slots__ = []
class Esc(Event):
    __slots__ = []
class Raw(Event):
    __slots__ = []
class _Resized(Event):
    __slots__ = []
Resized = _Resized("window resized")


class Terminal(object):
    MAX_IO_CHUNK = 16000
    
    def __init__(self, fd = sys.stdout):
        if hasattr(fd, "fileno"):
            fd.flush()
            fd = fd.fileno()
        self._fd = fd
        self.encoding = self._get_encoding()
        self._decoder = codecs.getincrementaldecoder(self.encoding)()
        self._raw_input = []
        self._processed_input = []
        self.cursor = CursorInfo(self)
    
    def __enter__(self):
        self.init()
        return self
    def __exit__(self, t, v, tb):
        self.restore()
    
    #=========================================================================
    # low level utilities
    #=========================================================================
    def _get_encoding(self):
        locale.setlocale(locale.LC_ALL, '')
        charset = None
        try:
            charset = locale.getpreferredencoding()
        except Exception:
            pass
        if charset:
            return charset
        try:
            charset = locale.nl_langinfo(locale.CODESET)
        except Exception:
            pass
        if charset:
            return charset
        return sys.getdefaultencoding()
    
    def _tty_set_cbreak(self, when = termios.TCSAFLUSH):
        mode = termios.tcgetattr(self._fd)
        mode[termios.LFLAG] = mode[termios.LFLAG] & ~(termios.ECHO | termios.ICANON)
        mode[termios.CC][termios.VMIN] = 1
        mode[termios.CC][termios.VTIME] = 0
        termios.tcsetattr(self._fd, when, mode)
    
    def _tty_reset_cbreak(self, when = termios.TCSAFLUSH):
        mode = termios.tcgetattr(self._fd)
        mode[termios.LFLAG] = mode[termios.LFLAG] & (termios.ECHO | termios.ICANON)
        termios.tcsetattr(self._fd, when, mode)

    def _write(self, data):
        data = data.encode(self.encoding)
        while data:
            chunk = data[:self.MAX_IO_CHUNK]
            try:
                count = os.write(self._fd, chunk)
            except OSError, ex:
                if ex.errno == errno.EINTR:
                    count = 0
                else:
                    raise
            data = data[count:]
    
    def _read(self, count):
        return os.read(self._fd, min(count, self.MAX_IO_CHUNK))
    
    def _wait_input(self, timeout = 0):
        if timeout is not None and timeout < 0:
            timeout = 0
        rl, _, _ = select.select([self._fd], [], [], timeout)
        return bool(rl)
    
    def _read_all(self, timeout = 0):
        data = []
        if timeout is not None:
            tend = time.time() + timeout
        while True:
            if timeout is None:
                remaining = None
            else:
                remaining = tend - time.time()
            self._wait_input(remaining)
            buf = self._read(100)
            if not buf:
                break
            data.append(buf)
            if timeout is not None and remaining < 0:
                break
        return "".join(data)
    
    def _tigetstr(self, cap):
        """string capabilities can include "delays" of the form "$<2>".
        for any modern terminal, strip them out."""
        val = curses.tigetstr(cap) or ''
        return re.sub(r'\$<\d+>[/*]?', '', val)

    def _sigwinch(self, *dummy):
        self._winch = True
        self._width = curses.tigetnum('cols')
        self._height = curses.tigetnum('lines')
        self.cursor._resized(self._width, self._height)

    #=========================================================================
    # init and restore
    #=========================================================================
    def init(self, exec_in_tty = True):
        if exec_in_tty and not os.isatty(self._fd):
            os.execl("/usr/bin/gnome-terminal", "-t", "python shell", "-x", 
                "/usr/bin/python", "-i", __file__, *sys.argv[1:])

        if not os.isatty(self._fd):
            raise ValueError("FD %d is not a tty" % (self._fd,))
        curses.setupterm()
        self._tty_set_cbreak()
        self._orig_winch = signal.signal(signal.SIGWINCH, self._sigwinch)
        self._sigwinch()
        self._init_caps()
        self.clear_screen()
        self.cursor.hide()
    
    def _init_caps(self):
        self._CURSOR_HIDE = self._tigetstr("civis")
        self._CURSOR_SHOW = self._tigetstr("cnorm")
        self._CURSOR_ADDRESS_template = self._tigetstr("cup")
        self._CLEAR_SCREEN = self._tigetstr("clear")
        self._ATTR_BLINK = self._tigetstr("blink")
        self._ATTR_BOLD = self._tigetstr("bold")
        self._ATTR_DIM = self._tigetstr("dim")
        self._ATTR_REVERSED = self._tigetstr("rev")
        self._ATTR_UNDERLINE = self._tigetstr("smul")
        self._ATTR_NORMAL = self._tigetstr("sgr0")
        self._ATTR_ITALICS = self._tigetstr("sitm")
        self._COLORS = self._init_colors("setaf", "setf")
        self._BG_COLORS = self._init_colors("setab", "setb")

    def _init_colors(self, ansi_cmd, native_cmd):
        ansi = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        native = ["black", "blue", "green", "cyan", "red", "magenta", "yellow", "white"]
        coll = dict((name, "") for name in ansi)
        template = self._tigetstr(ansi_cmd)
        if template:
            for i, name in enumerate(ansi):
                coll[name] = curses.tparm(template, i)
        else:
            template = self._tigetstr(native_cmd)
            if template:
                for i, name in enumerate(ansi):
                    coll[name] = curses.tparm(template, i)
        return coll
    
    def restore(self):
        self.cursor.show()
        self.clear_attrs()
        self._tty_reset_cbreak()
        signal.signal(signal.SIGWINCH, self._orig_winch)

    #=========================================================================
    # APIs
    #=========================================================================
    def get_size(self):
        return self._width, self._height
    
    def set_color(self, name):
        self._write(self._COLORS[name])
    def set_bg_color(self, name):
        self._write(self._BG_COLORS[name])
    def set_bold(self):
        self._write(self._ATTR_BOLD)
    def set_italics(self):
        self._write(self._ATTR_ITALICS)
    def set_underline(self):
        self._write(self._ATTR_UNDERLINE)
    def set_blink(self):
        self._write(self._ATTR_BLINK)
    def set_reversed(self):
        self._write(self._ATTR_REVERSED)
    def set_dim(self):
        self._write(self._ATTR_DIM)
    
    def clear_attrs(self):
        self._write(self._ATTR_NORMAL)
    
    def clear_screen(self):
        self._write(self._CLEAR_SCREEN)
        self.cursor._set(0, 0)
    
    def draw_hline(self, x, y, length):
        if x + length > self._width:
            length = self._width - x
        self.cursor.write(u"\u2500" * length, (x, y))

    def draw_vline(self, x, y, length):
        if y + length > self._height:
            length = self._height - y
        for i in range(length):
            self.cursor.write(u"\u2502", (x, y + i))
    
    def draw_box(self, x, y, w, h):
        self.draw_hline(x, y, w)
        self.draw_hline(x, y + h, w)
        self.draw_vline(x, y, h)
        self.draw_vline(x + w, y, h)
        self.cursor.write(u"\u250C", (x, y))
        self.cursor.write(u"\u2510", (x+w, y))
        self.cursor.write(u"\u2514", (x, y+h))
        self.cursor.write(u"\u2518", (x+w, y+h))
    
    #=========================================================================
    # Events
    #=========================================================================
    def _collect_raw_input(self, timeout):
        try:
            self._wait_input(timeout)
            data = self._read_all(0)
        except OSError, ex:
            if ex.errno == errno.EINTR:
                if self._winch:
                    self._winch = False
                    self._processed_input.append(Resized)
                return
            else:
                raise
        
        decoded = self._decoder.decode(data)
        if decoded:
            self._raw_input.append(decoded)
    
    def _get_processed_input(self):
        while not self._processed_input:
            seq = self._raw_input.pop(0)
            if len(seq) == 1:
                evt = Char(seq)
            elif len(seq) > 1 and seq[0] == "\x1b":
                evt = Esc(seq[1:])
            else:
                evt = Raw(seq)
            self._processed_input.append(evt)
        return self._processed_input.pop(0)
    
    def get_event(self, timeout = None):
        self._collect_raw_input(0)
        while not self._raw_input:
            self._collect_raw_input(timeout)
        return self._get_processed_input()


if __name__ == "__main__":
    with Terminal() as t:
        t.draw_box(5, 5, 20, 10)
        t.draw_box(65, 5, 1, 1)
        t.cursor.write("hello there", (8, 8))
        while True:
            print t.get_event()














