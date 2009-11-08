class Canvas(object):
    def write(self, data):
        pass

class Cursor(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.curr = dict(fg = None, bg = None, pos = (0, 0), bold = False, 
            underline = False)
        self.new = self.curr.copy()
    
    def move(self, x, y):
        self.new["pos"] = (x, y)
    
    def color(self, fg = None, bg = None):
        if fg:
            self.new["fg"] = fg
        if bg:
            self.new["bg"] = fg
    
    def bold(self, mode):
        self.new["bold"] = bool(mode)

    def underline(self, mode):
        self.new["underline"] = bool(mode)
    
    def write(self, text):
        need_clear = False
        for key, newval in self.new.iteritems():
            if self.curr[key] != newval:
                self.curr[key] = newval
                need_clear = True
        self.new.clear()
        if need_clear:
            self.canvas.clear_attrs()
        for 
        if self.curr["fg"]:
            self.canvas.set_fg_color(self.curr["fg"])
        if self.curr["bg"]:
            self.canvas.set_fg_color(self.curr["fg"])






























