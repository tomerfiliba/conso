import sys
import os
import re
import curses
import termios
import locale
import signal
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
        CURSOR_MOVE = lambda x, y, _template = _tigetstr("cup"): 
            curses.tparm(_template, y, x),
        CLEAR = _tigetstr("clear"),
        BLINK = _tigetstr("blink"),
        BOLD = _tigetstr("bold"),
        DIM = _tigetstr("dim"),
        REVERSED = _tigetstr("rev"),
        UNDERLINE = _tigetstr("smul"),
        RESET_ATTRS = _tigetstr("sgr0"),
        FG_COLORS = _init_colors("setaf", "setf"),
        BG_COLORS = _init_colors("setab", "setb"),
    )
    return caps

def get_terminal_size():
    return curses.tigetnum('cols'), curses.tigetnum('lines')

@contextmanager
def sigwinch(func):
    orig = signal.signal(signal.SIGWINCH, func)
    try:
        yield
    finally:
        signal.signal(signal.SIGWINCH, orig)







