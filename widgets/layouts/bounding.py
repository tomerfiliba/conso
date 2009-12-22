class BoundingBox(Widget):
    def __init__(self, body, min_width = 0, min_height = 0, max_width = None, max_height = None):
        self.body = body
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height

    def get_min_size(self, pwidth, pheight):
        w, h = self.body.get_min_size(pwidth, pheight)
        return (max(w, self.min_width), max(h, self.min_height))
    def get_desired_size(self, pwidth, pheight):
        w, h = self.body.get_desired_size(pwidth, pheight)
        return (min(w, self.max_width), min(h, self.max_height))
    
    def is_interactive(self):
        return self.body.is_interactive()
    def remodel(self, canvas):
        self.body.remodel(canvas)
    def render(self, style, focused = False, highlight = False):
        self.body.render(style, focused = focused, highlight = highlight)
    def on_event(self, evt):
        return self.body.on_event(evt)




