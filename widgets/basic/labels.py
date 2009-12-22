from ..base import Widget


class Label(Widget):
    __slots__ = ["text"]
    def __init__(self, text):
        self.text = text
    def get_min_size(self, pwidth, pheight):
        return (max(3, len(self.text)), 1)
    def get_desired_size(self, pwidth, pheight):
        return (len(self.text), 1)
    def is_interactive(self):
        return False
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, style, focused = False, highlight = False):
        padded = self.text + " " * (self.canvas.width - len(self.text))
        self.canvas.write(0, 0, padded, fg = style.label_text_color, bg = style.label_bg_color,
            inversed = highlight)

class LabelBox(Widget):
    def __init__(self, lines):
        self.lines = lines
        self.scroll_x = 0
        self.line_index = 0
    def get_min_size(self, pwidth, pheight):
        return (5, 2)
    def get_desired_size(self, pwidth, pheight):
        return (max(len(l) for l in self.lines)+2, len(self.lines))
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, style, focused = False, highlight = False):
        for y, line in enumerate(self.lines[self.line_index:self.line_index+self.canvas.height]):
            text = line[self.scroll_x:self.scroll_x+self.canvas.width]
            self.canvas.write(0, y, text, fg = style.labelbox_text_color, 
                bg = style.labelbox_bg_color)

    def _on_key(self, evt):
        if evt == "home":
            self.scroll_x = 0
            self.line_index = 0
            return True
        if evt == "end":
            self.line_index = max(len(self.lines) - 1, 0)
            return True
        elif evt == "up":
            self.line_index = max(0, self.line_index - 1)
            return True
        elif evt == "down":
            self.line_index = min(len(self.lines) - 1, self.line_index + 1)
            return True
        elif evt == "pagedown":
            self.line_index = min(len(self.lines) - 1, self.line_index + self.canvas.height)
            return True
        elif evt == "pageup":
            self.line_index = max(0, self.line_index - self.canvas.height)
            return True
        elif evt == "right":
            self.scroll_x += 1
            return True
        elif evt == "left":
            self.scroll_x = max(0, self.scroll_x - 1)
            return True
        return False


