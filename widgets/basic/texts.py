from ..base import Widget


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
            
            self.canvas.write(0, 0, before, fg = style.textentry_text_color_focused,
                bg = style.textentry_bg_color, inversed = highlight)
            self.canvas.write(len(before), 0, under, fg = style.textentry_text_color_focused,
                bg = style.textentry_bg_color, underlined = True, inversed = highlight)
            self.canvas.write(len(before) + 1, 0, after, fg = style.textentry_text_color_focused,
                bg = style.textentry_bg_color, inversed = highlight)
        else:
            self.canvas.write(0, 0, visible, fg = style.textentry_text_color, 
                bg = style.textentry_bg_color, inversed = highlight)
    
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

    def _on_mouse(self, evt):
        if evt.btn == evt.BTN_RELEASE:
            off = self.start_offset + evt.x
            #end = len(self.text) - self.start_offset
            self.cursor_offset = min(off, self.end_offset)
            return True
        return False

class TextBox(Widget):
    def __init__(self, lines = (), max_length = None):
        self.lines = list(lines)
        if not self.lines:
            self.lines.append("")
        self.max_length = max_length
        self.start_offset = 0
        self.end_offset = 0
        self.selected_line = 0


