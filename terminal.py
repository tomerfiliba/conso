import sys
import os
import termcntl
import errno
import codecs
from contextlib import contextmanager
from select import select
from canvas import TerminalCanvas


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
    
    def __init__(self, fd, caps, encoding):
        self.fd = fd
        self.caps = caps
        self.encoding = encoding
        self.canvas = TerminalCanvas(self)
        self._decoder = codecs.getincrementaldecoder(self.encoding)()
        self._events = []
        self._sigwinch()
    
    def _sigwinch(self, *dummy):
        self._events.append(Resized)
        self._width, self._height = termcntl.get_terminal_size()
        self.canvas._resized(self._width, self._height)

    #=========================================================================
    # IO
    #=========================================================================
    def _write(self, data):
        data = data.encode(self.encoding)
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
        return os.read(self._fd, min(count, self.MAX_IO_CHUNK))
    
    def _wait_input(self, timeout = None):
        if timeout is not None and timeout < 0:
            timeout = 0
        rl, _, _ = select([self._fd], [], [], timeout)
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

    #===============================================================================
    # API
    #===============================================================================
    def hide_cursor(self):
        self.cursor_visible = False
        self._write(self.caps["CURSOR_HIDE"])
    def show_cursor(self):
        self.cursor_visible = True
        self._write(self.caps["CURSOR_SHOW"])
    def get_size(self):
        return self._width, self._height
    
    #=========================================================================
    # Events
    #=========================================================================
    def get_event(self, timeout = None):
        self._wait_input(timeout)
        data = self._read_all()
        output = self._decoder.decode(data)
        if not output:
            self._events.append(None)
        elif len(output) == 1:
            self._events.append(Char(output))
        elif len(output) > 1 and output[0] == "\x1b":
            self._events.append(Esc(output[1:]))
        else:
            self._events.append(Raw(output))
        # note that we might have a queued Resized event here as well
        return self._events.pop(0)


@contextmanager
def setup_terminal(fd = sys.stdout, exec_in_tty = True):
    if hasattr(fd, "fileno"):
        fd.flush()
        fd = fd.fileno()
    if exec_in_tty and not os.isatty(fd):
        os.execl("/usr/bin/gnome-terminal", "-t", "python shell", "-x", 
            "/usr/bin/python", "-i", __file__, *sys.argv[1:])
    encoding = termcntl.get_encoding()
    caps = termcntl.get_terminal_capabilities(fd)
    term = Terminal(fd, caps, encoding)
    with termcntl.cbreak(fd):
        with termcntl.sigwinch(term._sigwinch):
            yield term




if __name__ == "__main__":
    with setup_terminal() as t:
        t.canvas.draw_box(5, 5, 50, 10)
        t.canvas.move_cursor(6,6)
        t.canvas.write("hello")









