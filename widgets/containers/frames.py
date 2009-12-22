from ..base import Widget


class Frame(Widget):
    __slots__ = ["title", "body"]
    def __init__(self, body, title = ""):
        self.title = title
        self.body = body
    def is_interactive(self):
        return self.body.is_interactive()
    def get_min_size(self, pwidth, pheight):
        w, h = self.body.get_min_size(pwidth-2, pheight-2)
        return w+2, h+2
    def get_desired_size(self, pwidth, pheight):
        w, h = self.body.get_desired_size(pwidth-2, pheight-2)
        return w+2, h+2
    def get_priority(self):
        return self.body.get_priority()
    def remodel(self, canvas):
        self.canvas = canvas
        self.body.remodel(canvas.subcanvas(1, 1, canvas.width-2, canvas.height-2))
    def render(self, style, focused = False, highlight = False):
        self.canvas.draw_border(
            fg = style.frame_border_color_focused if focused else style.frame_border_color)
        self.canvas.write(1,0,self.title[:self.canvas.width-2], 
            fg = style.frame_title_color_focused if focused else style.frame_title_color)
        self.body.render(style, focused = focused)
    def on_event(self, evt):
        return self.body.on_event(evt)


class StubBox(Widget):
    __slots__ = ["body"]
    def __init__(self, body = None):
        self.body = body
    def set(self, body):
        if self.body:
            raise ValueError("already set; call unset first")
        self.body = body
    def unset(self):
        self.body = None
    def is_set(self):
        return self.body is not None
    
    def is_interactive(self):
        if not self.body:
            return False
        return self.body.is_interactive()
    def get_min_size(self, pwidth, pheight):
        if not self.body:
            return (0, 0)
        return self.body.get_min_size(pwidth, pheight)
    def get_desired_size(self, pwidth, pheight):
        if not self.body:
            return (0, 0)
        return self.body.get_desired_size(pwidth, pheight)
    def remodel(self, canvas):
        if not self.body:
            return
        self.body.remodel(canvas)
    def render(self, style, focused = False, highlight = False):
        if not self.body:
            return
        self.body.render(style, focused = focused, highlight = highlight)
    def on_event(self, evt):
        if self.body:
            return self.body.on_event(evt)
        else:
            return False








