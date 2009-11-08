import sys
import os
import curses
import termios
import locale
from contextlib import contextmanager


_termios_IFLAG = 0
_termios_OFLAG = 1
_termios_CFLAG = 2
_termios_LFLAG = 3
_termios_ISPEED = 4
_termios_OSPEED = 5
_termios_CC = 6

@contextmanager
def cbreak(fd, when = termios.TCSAFLUSH):
    orig_mode = termios.tcgetattr(fd)
    mode = termios.tcgetattr(fd)
    mode[_termios_LFLAG] = mode[_termios_LFLAG] & ~(termios.ECHO | termios.ICANON)
    mode[_termios_CC][termios.VMIN] = 1
    mode[_termios_CC][termios.VTIME] = 0
    termios.tcsetattr(fd, when, mode)
    try:
        yield
    finally:
        termios.tcsetattr(fd, when, orig_mode)

def get_encoding():
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

def _tigetstr(cap):
    val = curses.tigetstr(cap) or ''
    return re.sub(r'\$<\d+>[/*]?', '', val)

def _init_colors(ansi_cmd, native_cmd):
    ansi = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    native = ["black", "blue", "green", "cyan", "red", "magenta", "yellow", "white"]
    coll = dict((name, "") for name in ansi)
    template = _tigetstr(ansi_cmd)
    if template:
        for i, name in enumerate(ansi):
            coll[name] = curses.tparm(template, i)
    else:
        template = _tigetstr(native_cmd)
        if template:
            for i, name in enumerate(ansi):
                coll[name] = curses.tparm(template, i)
    return coll

def get_terminal_capabilities(fd, type = None):
    if not type:
        type = os.getenv("TERM")
    curses.setupterm(type, fd)
    caps = dict(
        CURSOR_HIDE = _tigetstr("civis"),
        CURSOR_SHOW = _tigetstr("cnorm"),
        CURSOR_MOVE = _tigetstr("cup"),
        CLEAR_SCREEN = _tigetstr("clear"),
        ATTR_BLINK = _tigetstr("blink"),
        ATTR_BOLD = _tigetstr("bold"),
        ATTR_DIM = _tigetstr("dim"),
        ATTR_REVERSED = _tigetstr("rev"),
        ATTR_UNDERLINE = _tigetstr("smul"),
        ATTR_NORMAL = _tigetstr("sgr0"),
        ATTR_ITALICS = _tigetstr("sitm"),
        COLORS = _init_colors("setaf", "setf"),
        BG_COLORS = _init_colors("setab", "setb"),
    )
    return caps


@contextmanager
def get_terminal(fd = sys.stdout, exec_in_tty = True):
    if hasattr(fd, "fileno"):
        fd = fd.fileno()
    if exec_in_tty and not os.isatty(fd):
        os.execl("/usr/bin/gnome-terminal", "-t", "python shell", "-x", 
            "/usr/bin/python", "-i", __file__, *sys.argv[1:])
    encoding = get_encoding()
    caps = get_terminal_capabilities
    with cbreak(fd):
        yield Terminal(fd, encoding)

class Canvas(object):
    def write(self, data):
        pass

class Cursor(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.curr_fg_color = None
        self.curr_bg_color = None
        self.changed_fg_color = None
        self.changed_bg_color = None
    def move(self, x, y):
        pass
    def color(self, fg = None, bg = None):
        if fg:
            self.changed_fg_color = fg
        if bg:
            self.changed_fg_color = fg
    def write(self, text):
        if self.curr_bg_color != self.changed_fg_color:
            self.curr_bg_color = self.changed_fg_color

class TerminalCanvas(Canvas):
    def __init__(self, fd):
        self.fd = fd
    def write(self):
        pass


class TerminalCursor(object):
    def __init__(self, terminal):
        self.terminal = terminal
        self._x = 0
        self._y = 0
        self._visible = True
    
    def _set(self, x, y):
        self._x = x
        self._y = y
    def _resized(self, width, height):
        self._x = min(self._x, width)
        self._y = min(self._y, height)

    x = property(lambda self: self._x)
    y = property(lambda self: self._x)
    visible = property(lambda self: self._visible)

    def move(self, x, y):
        self.terminal._write(curses.tparm(self.terminal._CURSOR_ADDRESS_template, y, x))
    def hide(self):
        self.terminal._write(self.terminal._CURSOR_HIDE)
        self._visible = False
    def show(self):
        self.terminal._write(self.terminal._CURSOR_SHOW)
        self._visible = True
    
    def write(self, text, pos = None):
        if pos is not None:
            x, y = pos
            self.move(x, y)
        self.terminal._write(text)
        offset = self._x + len(text)
        self._x = offset % self.terminal._width
        self._y = max(self._y + offset // self.terminal._width, self.terminal._height - 1)


class TerminalCanvas(object):
    def __init__(self):
        pass
    def _write(self):
        pass

class Terminal(object):
    def __init__(self, fd, encoding):
        self.fd = fd
        self.encoding = encoding
        self.cursor = TerminalCursor(self)
    
    #==========================================================================
    # internal functions
    #==========================================================================
    def _write(self, data):
        pass
    
    def _read(self, count):
        pass
    
    def _wait_for_input(self, timeout = None):
        pass
    
    def _read_all(self):
        pass
    
    #==========================================================================
    # APIs
    #==========================================================================
    def draw_canvas(self, canvas):
        pass
    def get_event(self, timeout = None):
        pass








































