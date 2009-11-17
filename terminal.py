import sys
import os
import signal
import fcntl
import struct
import errno
import select
import curses
import termios
import locale
import re
import codecs
import tty
from events import ResizedEvent, terminal_keys_trie
from canvas import RootCanvas


class NoopCodec(object):
    __slots__ = []
    @staticmethod
    def encode(data):
        return data, len(data)
    @staticmethod
    def decode(data):
        return data
NoopCodec = NoopCodec()


class Terminal(object):
    MAX_IO_CHUNK = 16000
    
    def __init__(self, fd = sys.stdout, termtype = None, exec_in_tty = True, 
            raw_mode = True, use_mouse = False):
        if hasattr(fd, "fileno"):
            fd.flush()
            fd = fd.fileno()
        self.fd = fd
        self.encoding = self._get_encoding().lower()
        self._exec_in_tty = exec_in_tty
        self._termtype = termtype
        self._raw_mode = raw_mode
        self._use_mouse = use_mouse
        # state
        self._events = []
        if not self.encoding or self.encoding == "ascii":
            self._decoder = NoopCodec
            self._encoder = NoopCodec.encode
        else:
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
        if self._raw_mode:
            tty.setraw(self.fd)
        else:
            tty.setcbreak(self.fd)
    
    def _leave_cbreak(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self._orig_termios_mode)
    
    def _enter_keypad(self):
        self._write(self._tigetstr("smkx"))

    def _leave_keypad(self):
        self._write(self._tigetstr("rmkx"))
    
    def _enter_mouse_mode(self):
        self._write("\x1b[?1000;h")
    
    def _leave_mouse_mode(self):
        self._write("\x1b[?1000;l")
    
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
        self.RESET_ATTRS = self._tigetstr("sgr0")
        self.TEXT_ATTRS = dict(
            bold = self._tigetstr("bold"),
            blink = self._tigetstr("blink"),
            dim = self._tigetstr("dim"),
            inversed = self._tigetstr("rev"),
            underlined = self._tigetstr("smul"),
            fg = self._init_colors("setaf", "setf"),
            bg = self._init_colors("setab", "setb"),
        )

    def _get_size(self):
        buf = fcntl.ioctl(self.fd, termios.TIOCGWINSZ, "abcd")
        h, w = struct.unpack('hh', buf)
        return w, h

    def _sigwinch(self, *dummy):
        if ResizedEvent not in self._events:
            self._events.append(ResizedEvent)
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
                    "/usr/bin/python", "-i", *sys.argv)
            else:
                raise ValueError("fd must be a tty")

        self._init_caps()
        self._orig_sigwinch = signal.signal(signal.SIGWINCH, self._sigwinch)
        self._sigwinch()
        self._enter_cbreak()
        self._leave_keypad()
        if self._use_mouse:
            self._enter_mouse_mode()
        self.clear_screen()
        self.reset_attrs()
        self.hide_cursor()
        self._initialized = True
    
    def restore(self):
        if not self._initialized:
            raise ValueError("not initialized")
        signal.signal(signal.SIGWINCH, self._orig_sigwinch)
        if self._use_mouse:
            self._leave_mouse_mode()
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

    def set_title(self, title):
        self._write("\x1b]2;%s\x07" % (title,))

    def clear_screen(self):
        self._write(self.CLEAR_SCREEN)
    
    def get_size(self):
        return self._width, self._height
    
    def get_event(self, timeout = None):
        if not self._events:
            self._wait_input(timeout)
        data = self._read_all()
        output = self._decoder.decode(data)
        if output:
            self._events.extend(terminal_keys_trie.decode(output))
        
        # note that we might have a queued ResizedEvent event here as well
        return self._events.pop(0) if self._events else None

    def write(self, x, y, text, attrs = {}):
        reset = False
        caps = [self.CURSOR_MOVE(x, y)]
        for key, val in self._attrs.iteritems():
            new = attrs.get(key, None)
            if new != val:
                reset = True
                self._attrs[key] = new
                if new:
                    if type(new) is bool:
                        caps.append(self.TEXT_ATTRS[key])
                    else:
                        caps.append(self.TEXT_ATTRS[key][new])
        if reset:
            caps.insert(0, self.RESET_ATTRS)
        text2 = [ch if ord(ch) >= 32 else u"\ufffd" for ch in text]
        data = "".join(caps) + "".join(text2)
        self._write(data)

    def reset_attrs(self):
        self._attrs = dict(fg = None, bg = None, underlined = False,
            bold = False, inversed = False, dim = False)
        self._write(self.RESET_ATTRS)
    
    def get_root_canvas(self):
        return RootCanvas(self, self._width, self._height)



if __name__ == "__main__":
    with Terminal(use_mouse = True) as t:
#        while True:
#            t._wait_input()
#            x = t._read_all()
#            if x == "q":
#                break
#            t.clear_screen()
#            t.write(0, 0, repr(x))
        i = 0
        while True:
            evt = t.get_event()
            if evt == "ctrl q":
                break
            if i >= t._height:
                t.clear_screen()
                i = 0
            t.write(0, i, str(evt), dict(fg = "blue" if i % 2 else "red"))
            i += 1





