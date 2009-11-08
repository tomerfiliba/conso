import sys
import os


class Canvas(object):
    def __init__(self, caps):
        self.caps = caps
        self.attrs = {}
        self.new_attrs = {}
        self.reset_attrs()
        self.clear()
    
    def clear(self):
        self.cursor_pos = (0, 0)
        self.new_cursor_pos = None
        self._write(self.caps["CLEAR"])

    def set_color(self, fg = None, bg = None):
        if fg:
            self.new_attrs["fg"] = self.caps["FG_COLORS"][fg]
        if bg:
            self.new_attrs["bg"] = self.caps["BG_COLORS"][bg]
    def set_bold(self, mode):
        self.new_attrs["bold"] = self.caps["BOLD"] if mode else None
    def set_reversed(self, mode):
        self.new_attrs["reversed"] = self.caps["REVERSED"] if mode else None
    def set_underlined(self, mode):
        self.new_attrs["underlined"] = self.caps["UNDERLINED"] if mode else None
    def reset_attrs(self):
        self.attrs.update(fg = None, bg = None, underlined = False,
            bold = False, reversed = False)
        self.new_attrs.clear()
    
    def move_cursor(self, x, y):
        self.new_cursor_pos = (x, y)
    
    def _write(self, data):
        raise NotImplementedError()

    #=========================================================================
    # APIs
    #=========================================================================
    def write(self, text):
        changed = False
        for key in self.new_attrs:
            if self.attrs[key] != self.new_attrs[key]:
                self.attrs[key] = self.new_attrs[key]
                changed = True
        self.new_attrs.clear()
        caps = []
        if changed:
            caps.append(self.caps["RESET_ATTRS"])
            caps.extend(cap for cap in self.attrs.values() if cap)
        if self.new_cursor_pos is not None and self.cursor_pos != self.new_cursor_pos:
            self.cursor_pos = self.new_cursor_pos
            self.new_cursor_pos = None
            x, y = self.cursor_pos
            caps.append(self.caps["CURSOR_MOVE"](x, y))
        data = "".join(caps) + text
        x, y = self.cursor_pos
        self.cursor_pos = (x, y)
        self._write(data)

    def draw_hline(self, x, y, length):
        #if x + length > self._width:
        #    length = self._width - x
        self.move_cursor(x, y)
        self.write(u"\u2500" * length)

    def draw_vline(self, x, y, length):
        #if y + length > self._height:
        #    length = self._height - y
        for i in range(length):
            self.move_cursor(x, y + i)
            self.write(u"\u2502")
    
    def draw_box(self, x, y, w, h):
        self.draw_hline(x, y, w)
        self.draw_hline(x, y + h, w)
        self.draw_vline(x, y, h)
        self.draw_vline(x + w, y, h)
        self.move_cursor(x, y)
        self.write(u"\u250C")
        self.move_cursor(x+w, y)
        self.write(u"\u2510")
        self.move_cursor(x, y+h)
        self.write(u"\u2514")
        self.move_cursor(x+w, y+h)
        self.write(u"\u2518")

    def get_buffer(self):
        raise NotImplementedError()


class TerminalCanvas(Canvas):
    def __init__(self, terminal):
        self.terminal = terminal
        Canvas.__init__(self, terminal.caps)
    
    def _write(self, data):
        self.terminal._write(data)
    
    def copy(self, other_canvas):
        self._write(other_canvas.get_buffer())
        self.cursor_pos = other_canvas.cursor_pos

    def _resized(self, width, height):
        pass

class MemoryCanvas(Canvas):
    def __init__(self, caps):
        Canvas.__init__(self, caps)
        self.buffer = []
    
    def clear(self):
        self.buffer = ""
        Canvas.clear(self)
    
    def _write(self, data):
        self.buffer.append(data)

    def get_buffer(self):
        self.buffer = ["".join(self.buffer)]
        return self.buffer[0]





