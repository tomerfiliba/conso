from terminal import Terminal
from events import KeyEvent, MouseEvent, ResizedEvent


class RootCanvas(object):
    EMPTY_CHAR = (" ", None)
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.new_buffer = self._get_empty_buffer()
        self.old_buffer = self._get_empty_buffer()
    
    @classmethod
    def from_terminal(cls, term):
        w, h = term.get_size()
        return cls(w, h)

    def _get_empty_buffer(self):
        return [[self.EMPTY_CHAR] * self.width for i in range(self.height)]
    
    def commit(self, term):
        for y in range(self.height):
            for x in range(self.width):
                new = self.new_buffer[y][x]
                old = self.old_buffer[y][x]
                if new != old:
                    ch, attrs = new
                    if attrs:
                        term.set_attrs(**attrs)
                    else:
                        term.reset_attrs()
                    term.write(x, y, ch)
        self.old_buffer = self.new_buffer
        self.new_buffer = self._get_empty_buffer()
    
    def write(self, x, y, text, attrs = None):
        if y < 0 or y >= self.height:
            return
        for ch in text:
            if x < 0:
                x += 1
                continue
            if x >= self.width:
                break
            self.new_buffer[y][x] = (ch, attrs)
            x += 1
    
    def subcanvas(self, offx = 0, offy = 0, width = -1, height = -1):
        width = max(self.width - offx if width == -1 else width, 0)
        height = max(self.height - offy if height == -1 else height, 0)
        return Canvas(self, offx, offy, width, height)

class Canvas(object):
    __slots__ = ["parent", "offx", "offy", "width", "height"]
    def __init__(self, parent, offx, offy, width, height):
        self.parent = parent
        self.offx = offx
        self.offy = offy
        if width is not None:
            width = max(width, 0)
        self.width = width
        if height is not None:
            width = max(width, 0)
        self.height = height
    
    def write(self, x, y, text, attrs = None):
        if y < 0 or y > self.height and self.height is not None:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if self.width is not None:
            text = text[:self.width - x]
        if text:
            self.parent.write(x, y, text, attrs)

    def subcanvas(self, offx = 0, offy = 0, width = -1, height = -1):
        width = max(self.width - offx if width == -1 else width, 0)
        height = max(self.height - offy if height == -1 else height, 0)
        return Canvas(self, offx, offy, width, height)

    #=========================================================================
    # box drawing
    #=========================================================================
    def draw_hline(self, x, y, length, attrs):
        self.write(x, y, u"\u2500" * length, attrs)
    def draw_vline(self, x, y, length, attrs = None):
        for i in range(length):
            self.write(x, y + i, u"\u2502", attrs)
    def draw_box(self, x, y, w, h, attrs = None):
        self.draw_hline(x, y, w, attrs)
        self.draw_hline(x, y + h, w, attrs)
        self.draw_vline(x, y, h, attrs)
        self.draw_vline(x + w, y, h, attrs)
        self.write(x, y, u"\u250C", attrs)
        self.write(x+w, y, u"\u2510", attrs)
        self.write(x, y+h, u"\u2514", attrs)
        self.write(x+w, y+h, u"\u2518", attrs)
    def draw_border(self):
        self.draw_box(0, 0, self.width - 1, self.height - 1)
        return self.subcanvas(1, 1, self.width - 2, self.height - 2)
    


class Widget(object):
    def remodel(self, canvas):
        pass
    def render(self, canvas):
        pass



if __name__ == "__main__":
    with Terminal(use_mouse = False) as term:
        rc = RootCanvas.from_terminal(term)
        c = rc.subcanvas()
        while True:
            if term.get_event() == ResizedEvent:
                continue
            c2 = c.draw_border()
            c2.write(0, 0, "hello", dict(fg="red"))
            rc.commit(term)












