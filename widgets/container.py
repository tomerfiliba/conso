from .base import Widget
from . import simple


class Frame(Widget):
    def __init__(self, title, body):
        if not isinstance(title, Widget):
            title = simple.Label(title)
        self.title = title
        self.body = body
    def get_min_size(self, pwidth, pheight):
        w, h = self.body.get_min_size(pwidth-2, pheight-2)
        return w+2, h+2
    def get_desired_size(self, pwidth, pheight):
        w, h = self.body.get_desired_size(pwidth-2, pheight-2)
        return w+2, h+2
    def get_priority(self):
        return self.body.get_priority()
    def set_priority(self, priority):
        self.body.set_priority(priority)
    def remodel(self, canvas):
        self.canvas = canvas
        w, h = self.title.get_desired_size(self.canvas.width, self.canvas.height)
        self.title.remodel(canvas.subcanvas(1, 0, min(w, canvas.width-2), 1))
        self.body.remodel(canvas.subcanvas(1, 1, canvas.width-2, canvas.height-2))
    def render(self, focused = False, highlight = False):
        self.canvas.draw_border()
        self.title.render(highlight = highlight or focused)
        self.body.render(focused = focused)
    def on_event(self, evt):
        return self.body.on_event(evt)
    def is_interactive(self):
        return self.body.is_interactive()


class TabBox(Widget):
    def __init__(self, widgets, selected_index = 0):
        self.widgets = widgets
        self.selected_index = 0
        self.is_selected_focused = False
    
    def get_selected_widget(self):
        if selected_index < 0 or self.selected_index >= len(self.widgets):
            return None
        return self.widgets[self.selected_index]
    def get_min_size(self, pwidth, pheight):
        sw = self.get_selected_widget()
        if not sw:
            return (5, 4)
        w, h = sw.get_min_size(pwidth-2, pheight-3)
        return w + 2, h + 4
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, pheight)
    
    def remodel(self, canvas):
        self.canvas = canvas
        sw = self.get_selected_widget()
        if sw:
            sw.remodel(canvas)
    
    def render(self, focused = False, highlight = False):
        if self.border:
            self.canvas.draw_border()
            self.title.render(highlight = highlight or focused)
        self.body.render(focused = focused)
    
    def _on_key(self, evt):
        sw = self.get_selected_widget()
        if sw and sw.on_event(evt):
            return True
        
        if evt == "esc" and self.is_selected_focused:
            self.is_selected_focused = False
            return True
        elif evt == "tab":
            self.is_selected_focused = True
            return True
        elif evt == "shift tab":
            self.is_selected_focused = True
            return True
        return False


class ListModel(object):
    __slots__ = []
    def hasitem(self, index):
        raise NotImplementedError()
    def getitem(self, index):
        raise NotImplementedError()

class SimpleListModel(ListModel):
    __slots__ = ["list"]
    def __init__(self, list):
        self.list = [item if isinstance(item, Widget) else Label(str(item)) 
            for item in list]
    def hasitem(self, index):
        return index >= 0 and index < len(self.list)
    def getitem(self, index):
        return self.list[index]


class ListBox(Widget):
    def __init__(self, model):
        self.model = model
        self.start_index = 0
        self.last_index = None
        self.selected_index = 0
        self.hor_offset = 0
        self.is_selected_focused = False
    def get_min_size(self, pwidth, pheight):
        return (5, 2)
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, pheight)
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, focused = False, highlight = False):
        if self.selected_index < self.start_index or self.selected_index > self.last_index:
            self.last_index = None
            self.start_index = self.selected_index
        
        #self.canvas.draw_vline(0, 0, char = self.canvas.LEFT_HALF_BLOCK)
        #self.canvas.write(0, 0, u"\u2191")
        #self.canvas.write(0, self.canvas.height - 1, u"\u2193")
        #self.canvas.draw_hline(2, self.canvas.height - 1, char = self.canvas.LOWER_HALF_BLOCK)
        #self.canvas.write(1, self.canvas.height - 1, u"\u2190")
        #self.canvas.write(self.canvas.width - 1, self.canvas.height - 1, u"\u2192")

        offy = 0
        i = self.start_index
        while self.model.hasitem(i) and offy < self.canvas.height:
            self.last_index  = i
            item = self.model.getitem(i)
            dw, dh = item.get_desired_size(self.canvas.width, self.canvas.height)
            canvas2 = self.canvas.subcanvas(self.hor_offset, offy, dw, dh)
            item.remodel(canvas2)
            if i == self.selected_index:
                item.render(focused = focused and self.is_selected_focused, highlight = focused)
            else:
                item.render()
            i += 1
            offy += canvas2.height
    
    def _on_key(self, evt):
        if self.is_selected_focused:
            item = self.model.getitem(self.selected_index)
            if item.on_event(evt):
                return True
        
        if evt == "esc" and self.is_selected_focused:
            self.is_selected_focused = False
            return True
        elif evt == "down":
            if self.model.hasitem(self.selected_index + 1):
                self.is_selected_focused = False
                self.selected_index += 1
            return True
        elif evt == "up":
            if self.selected_index >= 1:
                self.is_selected_focused = False
                self.selected_index -= 1
            return True
        elif evt == "left":
            self.hor_offset += 1
            return True
        elif evt == "right":
            self.hor_offset -= 1
            return True
        elif evt == "home":
            self.selected_index = 0
            return True
        elif evt == "end":
            # XXX how do we handle this?
            return True
        elif evt == "pagedown":
            for i in range(1, self.canvas.height):
                if not self.model.hasitem(self.selected_index + 1):
                    break
                self.selected_index += 1
            self.is_selected_focused = False
            return True
        elif evt == "pageup":
            if self.selected_index >= 1:
                self.selected_index = max(0, self.selected_index - self.canvas.height)
                self.is_selected_focused = False
            return True
        elif evt == "enter":
            if self.model.hasitem(self.selected_index):
                item = self.model.getitem(self.selected_index)
                if item.is_interactive():
                    self.is_selected_focused = True
            return True
        return False




