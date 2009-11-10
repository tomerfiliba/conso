import sys
import os
import signal
import errno
import select
import curses
import termios
import locale
import re
import codecs


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
class Resized(Event):
    __slots__ = []
Resized = Resized("window resized")

_termios_LFLAG = 3
_termios_CC = 6

class Terminal(object):
    MAX_IO_CHUNK = 16000
    
    def __init__(self, fd = sys.stdout, termtype = None, exec_in_tty = True):
        if hasattr(fd, "fileno"):
            fd.flush()
            fd = fd.fileno()
        self.fd = fd
        self.encoding = self._get_encoding()
        self._exec_in_tty = exec_in_tty
        self._termtype = termtype
        # state
        self._events = []
        self._decoder = codecs.getincrementaldecoder(self.encoding)("replace")
        self._encoder = codecs.getencoder(self.encoding)
        self._initialized = False
    
    def __enter__(self):
        self.setup()
        return self
    
    def __exit__(self, t, v, tb):
        self.restore()

    #=========================================================================
    # Low level terminal handling
    #=========================================================================
    @classmethod
    def _get_encoding(cls):
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

    @classmethod
    def _tigetstr(cls, cap):
        val = curses.tigetstr(cap) or ''
        return re.sub(r'\$<\d+>[/*]?', '', val)
    
    def _enter_cbreak(self):
        self._orig_termios_mode = termios.tcgetattr(self.fd)
        mode = termios.tcgetattr(self.fd)
        mode[_termios_LFLAG] = mode[_termios_LFLAG] & ~(termios.ECHO | termios.ICANON)
        mode[_termios_CC][termios.VMIN] = 1
        mode[_termios_CC][termios.VTIME] = 0
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, mode)
    
    def _leave_cbreak(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self._orig_termios_mode)
    
    @classmethod
    def _init_colors(cls, ansi_cmd, native_cmd):
        ansi = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        native = ["black", "blue", "green", "cyan", "red", "magenta", "yellow", "white"]
        coll = dict((name, "") for name in ansi)
        template = cls._tigetstr(ansi_cmd)
        if template:
            for i, name in enumerate(ansi):
                coll[name] = curses.tparm(template, i)
        else:
            template = cls._tigetstr(native_cmd)
            if template:
                for i, name in enumerate(ansi):
                    coll[name] = curses.tparm(template, i)
        return coll
    
    def _init_caps(self):
        curses.setupterm(self._termtype, self.fd)
        self.CURSOR_HIDE = self._tigetstr("civis")
        self.CURSOR_SHOW = self._tigetstr("cnorm")
        self.CURSOR_MOVE = lambda x, y, _template = self._tigetstr("cup"): curses.tparm(_template, y, x)
        self.CLEAR_SCREEN = self._tigetstr("clear")
        self.ATTR_BLINK = self._tigetstr("blink")
        self.ATTR_BOLD = self._tigetstr("bold")
        self.ATTR_DIM = self._tigetstr("dim")
        self.ATTR_INVERSED = self._tigetstr("rev")
        self.ATTR_UNDERLINE = self._tigetstr("smul")
        self.RESET_ATTRS = self._tigetstr("sgr0")
        self.FG_COLORS = self._init_colors("setaf", "setf")
        self.BG_COLORS = self._init_colors("setab", "setb")

    @classmethod
    def _get_size(cls):
        return curses.tigetnum('cols'), curses.tigetnum('lines')

    def _sigwinch(self, *dummy):
        self._events.append(Resized)
        self._width, self._height = self._get_size()

    #=========================================================================
    # IO
    #=========================================================================
    def _write(self, data):
        data = self._encoder(data)[0]
        while data:
            chunk = data[:self.MAX_IO_CHUNK]
            try:
                count = os.write(self.fd, chunk)
            except OSError, ex:
                if ex.errno == errno.EINTR:
                    count = 0
                else:
                    raise
            data = data[count:]
    
    def _read(self, count):
        return os.read(self.fd, min(count, self.MAX_IO_CHUNK))
    
    def _wait_input(self, timeout = None):
        if timeout is not None and timeout < 0:
            timeout = 0
        try:
            rl, _, _ = select.select([self.fd], [], [], timeout)
        except select.error, ex:
            if ex.args[0] == errno.EINTR:
                return False
            else:
                raise
        return bool(rl)
    
    def _read_all(self):
        data = []
        while self._wait_input(0):
            try:
                buf = self._read(500)
            except OSError, ex:
                if ex.errno == errno.EINTR:
                    break
                else:
                    raise
            if not buf:
                if not data:
                    raise EOFError()
                break
            data.append(buf)
        return "".join(data)

    #=========================================================================
    # APIs
    #=========================================================================
    def setup(self):
        if self._initialized:
            raise ValueError("already initialized")
        if not os.isatty(self.fd):
            if self._exec_in_tty:
                os.execl("/usr/bin/gnome-terminal", "-t", "python shell", "-x", 
                    "/usr/bin/python", "-i", __file__, *sys.argv[1:])
            else:
                raise ValueError("fd must be a tty")

        self._init_caps()
        self._orig_sigwinch = signal.signal(signal.SIGWINCH, self._sigwinch)
        self._sigwinch()
        self._enter_cbreak()
        self.clear_screen()
        self.reset_attrs()
        self.hide_cursor()
        self._initialized = True
    
    def restore(self):
        if not self._initialized:
            raise ValueError("not initialized")
        signal.signal(signal.SIGWINCH, self._orig_sigwinch)
        self._leave_cbreak()
        self.show_cursor()
        self.reset_attrs()
        self._initialized = False

    def hide_cursor(self):
        self._cursor_visible = False
        self._write(self.CURSOR_HIDE)
    
    def show_cursor(self):
        self._cursor_visible = True
        self._write(self.CURSOR_SHOW)

    def clear_screen(self):
        self._cursor_x = 0
        self._cursor_y = 0
        self._write(self.CLEAR_SCREEN)
    
    def get_size(self):
        return self._width, self._height

    def _process_raw_event(self, data):
        if len(data) == 1:
            return Char(data)
        elif len(data) > 1 and data[0] == "\x1b":
            return Esc(data[1:])
        else:
            return Raw(data)

    def get_event(self, timeout = None):
        if not self._events:
            self._wait_input(timeout)
        data = self._read_all()
        output = self._decoder.decode(data)
        if output:
            evt = self._process_raw_event(output)
            self._events.append(evt)
        
        # note that we might have a queued Resized event here as well
        if self._events:
            return self._events.pop(0)
        else:
            return None

    def write(self, text, x, y):
        changed = False
        for key in self._new_attrs:
            if self._curr_attrs[key] != self._new_attrs[key]:
                self._curr_attrs[key] = self._new_attrs[key]
                changed = True
        self._new_attrs.clear()
        caps = [self.CURSOR_MOVE(x, y)]
        if changed:
            caps.append(self.RESET_ATTRS)
            caps.extend(cap for cap in self._curr_attrs.values() if cap)
        data = "".join(caps) + text
        self._write(data)

    def set_attrs(self, fg = None, bg = None, bold = None, underlined = None, inversed = None):
        if fg is not None:
            self._new_attrs["fg"] = self.FG_COLORS[fg]
        if bg is not None:
            self._new_attrs["bg"] = self.BG_COLORS[bg]
        if bold is not None:
            self._new_attrs["bold"] = self.ATTR_BOLD if bold else None
        if underlined is not None:
            self._new_attrs["underlined"] = self.ATTR_UNDERLINE if underlined else None
        if inversed is not None:
            self._new_attrs["inversed"] = self.ATTR_INVERSED if inversed else None
    
    def reset_attrs(self):
        self._curr_attrs = dict(fg = None, bg = None, underlined = False,
            bold = False, inversed = False)
        self._new_attrs = {}
        self._write(self.RESET_ATTRS)
    
    def get_canvas(self, x, y, width, height):
        return Canvas(self, x, y, width, height)


class Canvas(object):
    def __init__(self, terminal, x, y, width, height):
        self.terminal = terminal
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.attrs = {}
    
    def write(self, text, x, y):
        if y > self.height or x > self.width:
            return
        self.terminal.set_attrs(**self.attrs)
        self.terminal.write(text[:self.width - x], self.x + x, self.y + y)
    def set_attrs(self, **kwargs):
        self.attrs.update(kwargs)

    def draw_hline(self, x, y, length):
        self.write(u"\u2500" * length, x, y)
    def draw_vline(self, x, y, length):
        for i in range(length):
            self.write(u"\u2502", x, y + i)
    def draw_box(self, x, y, w, h):
        self.draw_hline(x, y, w)
        self.draw_hline(x, y + h, w)
        self.draw_vline(x, y, h)
        self.draw_vline(x + w, y, h)
        self.write(u"\u250C", x, y)
        self.write(u"\u2510", x+w, y)
        self.write(u"\u2514", x, y+h)
        self.write(u"\u2518", x+w, y+h)
    def draw_borders(self):
        self.draw_box(0, 0, self.width-1, self.height)


if __name__ == "__main__":
    with Terminal() as t:
        c1 = t.get_canvas(12, 12, 50, 10)
        c2 = t.get_canvas(2, 2, 7, 7)
        c1.draw_borders()
        c2.draw_borders()
        c1.set_attrs(fg = "red")
        c2.set_attrs(fg = "yellow", bold = True)
        c1.write("hello", 1, 1)
        c2.write("worldxxxx", 1, 1)
        









