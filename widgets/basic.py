from .base import Widget


class Label(Widget):
    __slots__ = ["text", "fg", "bg"]
    def __init__(self, text, fg = None, bg = None):
        self.text = text
        self.fg = fg
        self.bg = bg
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
        self.canvas.write(0, 0, padded, fg = self.fg, bg = self.bg, inversed = highlight)

class TextEntry(Widget):
    def __init__(self, text = "", max_length = None):
        self.text = text
        self.max_length = max_length
        self.cursor_offset = 0
        self.start_offset = 0
        self.end_offset = 0
    def remodel(self, canvas):
        self.canvas = canvas
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, 1)
    def get_min_size(self, pwidth, pheight):
        return (3, 1)
    def render(self, style, focused = False, highlight = False):
        w = self.canvas.width
        
        if self.cursor_offset < self.start_offset or \
               self.cursor_offset >= self.end_offset or \
               (self.end_offset < self.start_offset + w and len(self.text) > self.end_offset):
            self.end_offset = min(len(self.text), self.cursor_offset + w)
            self.start_offset = max(0, self.end_offset - w)
        
        visible = self.text[self.start_offset:self.end_offset]
        
        if focused:
            visible += self.canvas.DOT * (w - len(visible))
            rel_cursor = max(0, self.cursor_offset - self.start_offset)
            if self.cursor_offset >= len(self.text) and rel_cursor >= w:
                before = visible[1:]
                under = self.canvas.DOT
                after = ""
            else:
                before = visible[:rel_cursor]
                under = visible[rel_cursor]
                after = visible[rel_cursor+1:]
            self.canvas.write(0, 0, before, inversed = highlight)
            self.canvas.write(len(before), 0, under, underlined = True, inversed = highlight)
            self.canvas.write(len(before) + 1, 0, after, inversed = highlight)
        else:
            self.canvas.write(0, 0, visible, inversed = highlight)
    
    def _on_key(self, evt):
        if evt == "left":
            if self.cursor_offset >= 1:
                self.cursor_offset -= 1
            return True
        elif evt == "right":
            if self.cursor_offset <= len(self.text) - 1:
                self.cursor_offset += 1
            return True
        elif evt == "backspace":
            if self.cursor_offset >= 1:
                before = self.text[:self.cursor_offset-1]
                after = self.text[self.cursor_offset:]
                self.cursor_offset -= 1
                self.text = before + after
            return True
        elif evt == "delete":
            if len(self.text) > self.cursor_offset:
                before = self.text[:self.cursor_offset]
                after = self.text[self.cursor_offset+1:]
                self.text = before + after
            return True
        elif evt == "home":
            self.cursor_offset = 0
            return True
        elif evt == "end":
            self.cursor_offset = len(self.text)
            return True
        elif not self.max_length or len(self.text) < self.max_length:
            ch = evt.as_char()
            if ch:
                before = self.text[:self.cursor_offset]
                after = self.text[self.cursor_offset:]
                self.text = before + ch + after
                self.cursor_offset += 1
                return True
        return False

class Button(Widget):
    def __init__(self, text, callback):
        self.text = text
        self.callback = callback
    def remodel(self, canvas):
        self.canvas = canvas
    def get_min_size(self, pwidth, pheight):
        return (3, 1)
    def get_desired_size(self, pwidth, pheight):
        return (len(self.text) + 2, 1)
    def render(self, style, focused = False, highlight = True):
        text = u"\u258C%s\u2590" % (self.text[:self.canvas.width-2],)
        self.canvas.write(0, 0, text, fg = "yellow" if focused else None)
    
    def _on_key(self, evt):
        if evt == "enter" or evt == "space":
            self.callback(self)
            return True
        return False

class ProgressBar(Widget):
    def __init__(self, percentage = 0, show_percentage = True):
        self.percentage = percentage
        self.show_percentage = show_percentage
    def get_min_size(self, pwidth, pheight):
        return (4, 1)
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, 1)
    def get_progress(self):
        return self.percentage
    def set_progress(self, percentage):
        if self.percentage < 0 or self.percentage > 100:
            raise ValueError("percentage must be in range 0..100")
        self.percentage = percentage
    def is_interactive(self):
        return False
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, style, focused = False, highlight = False):
        full = int((self.percentage * self.canvas.width) / 100)
        empty = self.canvas.width - full
        text = self.canvas.FULL_BLOCK * full + self.canvas.LIGHT_SHADE * empty
        if self.show_percentage and len(text) > 4:
            percentage = str(int(self.percentage))
            start = (len(text) - len(percentage)) // 2
            end = start + len(percentage)
            for i in range(len(text)):
                if start <= i < end:
                    if i < full:
                        self.canvas.write(i, 0, percentage[i - start], inversed = True)
                    else:
                        self.canvas.write(i, 0, percentage[i - start])
                else:
                    self.canvas.write(i, 0, text[i])
        else:
            self.canvas.write(0, 0, text)


class CheckButton(Widget):
    pass


class ChoiceButton(Widget):
    pass














