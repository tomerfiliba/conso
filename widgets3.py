from events import KeyEvent, MouseEvent


class Widget(object):
    def on_event(self, evt):
        if isinstance(evt, KeyEvent):
            return self._on_key(evt)
        elif isinstance(evt, MouseEvent):
            return self._on_mouse(evt)
        else:
            return False
    def _on_key(self, evt):
        return False
    def _on_mouse(self, evt):
        return False
    
    def get_min_size(self, pwidth, pheight):
        raise NotImplementedError()
    def get_desired_size(self, pwidth, pheight):
        raise NotImplementedError()
    def remodel(self, canvas):
        raise NotImplementedError()
    def render(self, focused = False, highlight = False):
        raise NotImplementedError()


class Label(Widget):
    def __init__(self, text, fg = None, bg = None):
        self.text = text
        self.fg = fg
        self.bg = bg
    def get_min_size(self, pwidth, pheight):
        return (max(3, len(text)), 1)
    def get_desired_size(self, pwidth, pheight):
        return (len(text), 1)
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, focused = False, highlight = False):
        padded = self.text + " " * (canvas.width - len(self.text))
        self.canvas.write(0, 0, padded, dict(fg = self.fg, bg = self.bg, inversed = highlight))

class TextEntry(Widget):
    def __init__(self, text = "", max_length = None):
        self.text = text
        self.max_length = max_length
        self.cursor_offset = 0
        self.start_offset = None
        self.end_offset = None
    def remodel(self, canvas):
        self.canvas = canvas
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, 1)
    def get_min_size(self, pwidth, pheight):
        return (3, 1)
    def render(self, focused = True, highlight = False):
        w = self.canvas.width
        
        if self.cursor_offset > self.end_offset or self.cursor_offset < self.start_offset:
            self.end_offset = min(len(self.text), self.cursor_offset + w)
            self.start_offset = max(0, self.end_offset - w)
        visible = self.text[self.start_offset:self.end_offset]
        
        if focused:
            rel_cursor = max(0, self.cursor_offset - self.start_offset)
            if rel_cursor >= len(visible):
                if len(self.text) >= w:
                    before = visible[1:]
                else:
                    before = visible
                under = self.canvas.DOT
                after = ""
            else:
                before = visible[:rel_cursor]
                under = visible[rel_cursor]
                after = visible[rel_cursor+1:]
            after += self.canvas.DOT * (w - len(visible) - 1)
            self.canvas.write(0, 0, before, dict(underlined = False, inversed = highlight))
            self.canvas.write(len(before), 0, under, dict(underlined = True, inversed = highlight))
            self.canvas.write(len(before) + 1, 0, after, dict(underlined = False, inversed = highlight))
        else:
            self.canvas.write(0, 0, visible, dict(inversed = highlight))
    
    def _on_key(self, evt):
        if evt == "left" and self.cursor_offset >= 1:
            self.cursor_offset -= 1
            return True
        elif evt == "right" and self.cursor_offset <= len(self.text) - 1:
            self.cursor_offset += 1
            return True
        elif evt == "backspace" and self.cursor_offset >= 1:
            before = self.text[:self.cursor_offset-1]
            after = self.text[self.cursor_offset:]
            self.cursor_offset -= 1
            self.text = before + after
            return True
        elif evt == "delete" and len(self.text) > self.cursor_offset:
            before = self.text[:self.cursor_offset]
            after = self.text[self.cursor_offset+1:]
            self.text = before + after
            return True
        elif evt == "home":
            self.cursor_offset = 0
        elif evt == "end":
            self.cursor_offset = len(self.text)
        elif not self.max_length or len(self.text) < self.max_length:
            ch = evt.as_char()
            if ch:
                before = self.text[:self.cursor_offset]
                after = self.text[self.cursor_offset:]
                self.text = before + ch + after
                self.cursor_offset += 1
                return True
        return False


class 




if __name__ == "__main__":
    from application import Application
    te = TextEntry()
    
    app = Application(te)
    app.run(exit = False)


















