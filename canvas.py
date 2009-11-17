class Canvas(object):
    __slots__ = ["parent", "offx", "offy", "width", "height"]
    
    LEFT_ARROW = u"\u00ab"
    RIGHT_ARROW = u"\u00bb"
    LIGHT_SHADE = u"\u2591"
    MEDIUM_SHADE = u"\u2592"
    DARK_SHADE = u"\u2593"
    FULL_BLOCK = u"\u2588"
    LOWER_HALF_BLOCK = u"\u2584"
    LEFT_HALF_BLOCK = u"\u258c"
    RIGHT_HALF_BLOCK = u"\u2590"
    UPPER_HALF_BLOCK = u"\u2580"
    HOR_LINE = u"\u2500"
    VER_LINE = u"\u2502"
    LEFT_UPPER_CORNER = u"\u250C"
    RIGHT_UPPER_CORNER = u"\u2510"
    LEFT_LOWER_CORNER = u"\u2514"
    RIGHT_LOWER_CORNER = u"\u2518"
    DOT = u"\u00B7"
    
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
    
    def write(self, x, y, text, **attrs):
        if y < 0 or y > self.height and self.height is not None:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if self.width is not None:
            text = text[:self.width - x]
        if text:
            self.parent.write(self.offx + x, self.offy + y, text, **attrs)

    def subcanvas(self, offx = 0, offy = 0, width = -1, height = -1):
        width = max(self.width - offx if width == -1 else width, 0)
        height = max(self.height - offy if height == -1 else height, 0)
        return Canvas(self, offx, offy, width, height)

    #=========================================================================
    # box drawing
    #=========================================================================
    def draw_hline(self, x, y, length, **attrs):
        self.write(x, y, self.HOR_LINE * length, **attrs)
    def draw_vline(self, x, y, length, attrs = None):
        for i in range(length):
            self.write(x, y + i, self.VER_LINE, **attrs)
    def draw_box(self, x, y, w, h, **attrs):
        self.draw_hline(x, y, w, **attrs)
        self.draw_hline(x, y + h, w, **attrs)
        self.draw_vline(x, y, h, **attrs)
        self.draw_vline(x + w, y, h, **attrs)
        self.write(x, y, self.LEFT_UPPER_CORNER, **attrs)
        self.write(x+w, y, self.RIGHT_UPPER_CORNER, **attrs)
        self.write(x, y+h, self.LEFT_LOWER_CORNER, **attrs)
        self.write(x+w, y+h, self.RIGHT_LOWER_CORNER, **attrs)
    def draw_border(self):
        self.draw_box(0, 0, self.width - 1, self.height - 1)
        return self.subcanvas(1, 1, self.width - 2, self.height - 2)
    
    def clear_line(self, y, **attrs):
        self.write(0, y, " " * self.width, **attrs)


class RootCanvas(Canvas):
    EMPTY_CHAR = (" ", None)
    def __init__(self, term, width, height):
        self.term = term
        self.width = width
        self.height = height
        self.new_buffer = self._get_empty_buffer()
        self.old_buffer = self._get_empty_buffer()
    
    def _get_empty_buffer(self):
        return [[self.EMPTY_CHAR] * self.width for i in range(self.height)]
    
    def commit(self):
        for y in range(self.height):
            for x in range(self.width):
                new = self.new_buffer[y][x]
                old = self.old_buffer[y][x]
                if new != old:
                    ch, attrs = new
                    self.term.write(x, y, ch, **attrs)
        self.old_buffer = self.new_buffer
        self.new_buffer = self._get_empty_buffer()
    
    def write(self, x, y, text, **attrs):
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


if __name__ == "__main__":
    from terminal import Terminal
    from events import KeyEvent, MouseEvent, ResizedEvent

    with Terminal(use_mouse = False) as term:
        rc = term.get_root_canvas()
        c = rc.subcanvas()
        c2 = c.draw_border()
        c2.write(0, 0, "hello     ", dict(fg="red", inversed = True))
        rc.commit()

        while True:
            if term.get_event() != ResizedEvent:
                break












