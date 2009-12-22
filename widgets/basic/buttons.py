from ..base import Widget


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
    def render(self, style, focused = False, highlight = False):
        text = u"[%s]" % (self.text[:self.canvas.width-2],)
        self.canvas.write(0, 0, text, 
            fg = style.button_text_color_focused if focused else style.button_text_color, 
            bg = style.button_bg_color, bold = True, inversed = highlight)
    
    def _on_key(self, evt):
        if evt == "enter" or evt == "space":
            self.callback(self)
            return True
        return False


class CheckButton(Widget):
    pass


class ChoiceButton(Widget):
    pass

