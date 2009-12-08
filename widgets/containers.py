from .base import Widget
from . import basic


class Frame(Widget):
    def __init__(self, title, body):
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
        self.canvas.draw_border()
        self.canvas.write(1,0,self.title[:self.canvas.width-2])
        self.body.render(style, focused = focused)
    def on_event(self, evt):
        return self.body.on_event(evt)


class TabInfo(object):
    __slots__ = ["title", "widget"]
    def __init__(self, title, widget):
        self.title = title
        self.widget = widget

class TabBox(Widget):
    def __init__(self, widgets, show_title = True, selected_index = 0):
        self.show_title = show_title
        self.tabs = tabs
        self.selected_index = 0
        self.is_selected_focused = False
    
    def get_selected_widget(self):
        if selected_index < 0 or self.selected_index >= len(self.tabs):
            return None
        return self.tabs[self.selected_index].widget
    def get_min_size(self, pwidth, pheight):
        sw = self.get_selected_widget()
        if not sw:
            if self.show_title:
                return (0, 0)
            else:
                return (0, 0)
        if self.show_title:
            w, h = sw.get_min_size(pwidth-2, pheight-3)
            return w + 2, h + 4
        else:
            w, h = sw.get_min_size(pwidth, pheight)
            return w, h
    
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, pheight)
    
    def remodel(self, canvas):
        self.canvas = canvas
        sw = self.get_selected_widget()
        if sw:
            sw.remodel(canvas)
    
    def render(self, style, focused = False, highlight = False):
        if self.border:
            self.canvas.draw_border()
            self.title.render(style, highlight = highlight or focused)
        self.body.render(style, focused = focused)
    
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
        self.list = list
    def hasitem(self, index):
        return index >= 0 and index < len(self.list)
    def getitem(self, index):
        item = self.list[index]
        if not isinstance(item, Widget):
            item = basic.Label(str(item))
        return item
    
    def append(self, item):
        self.list.append(item)
    def insert(self, index, item):
        self.list.insert(index, item)
    def pop(self, index = -1):
        self.list.pop(index)
    def __getitem__(self, index):
        return self.list[index]
    def __delitem__(self, index):
        del self.list[index]
    def __setitem__(self, index, item):
        self.list[index] = item

class ListBox(Widget):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, axis, model):
        assert isinstance(model, ListModel)
        self.axis = axis
        self.model = model
        self.start_index = 0
        self.last_index = None
        self.selected_index = 0
        self.scrolled_offset = 0
        self.is_selected_focused = False
        self.remodelling_required = True
    def get_min_size(self, pwidth, pheight):
        return (5, 1)
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, pheight)
    def remodel(self, canvas):
        self.canvas = canvas
        self.remodelling_required = True
    def render(self, style, focused = False, highlight = False):
        if self.selected_index < self.start_index or self.selected_index > self.last_index:
            self.last_index = None
            self.start_index = self.selected_index

        off = 0
        i = self.start_index
        self.remodelling_required = True
        size = self.canvas.width if self.axis == self.HORIZONTAL else self.canvas.height
        
        while self.model.hasitem(i) and off < size:
            self.last_index  = i
            item = self.model.getitem(i)
            dw, dh = item.get_desired_size(self.canvas.width, self.canvas.height)
            if self.remodelling_required:
                if self.axis == self.HORIZONTAL:
                    canvas2 = self.canvas.subcanvas(off, self.scrolled_offset, dw, dh)
                else:
                    canvas2 = self.canvas.subcanvas(self.scrolled_offset, off, dw, dh)
                item.remodel(canvas2)
            if i == self.selected_index:
                item.render(style, focused = focused and self.is_selected_focused, highlight = focused)
            else:
                item.render(style)
            i += 1
            off += dw if self.axis == self.HORIZONTAL else dh
        
        self.remodelling_required = False
    
    def _on_key(self, evt):
        if self.is_selected_focused:
            item = self.model.getitem(self.selected_index)
            if item.on_event(evt):
                return True
        
        if self.axis == self.HORIZONTAL:
            if evt == "down":
                evt = "right"
            elif evt == "up":
                evt = "left"
            elif evt == "right":
                evt = "down"
            elif evt == "up":
                evt = "left"
        
        if evt == "esc" and self.is_selected_focused:
            self.is_selected_focused = False
            #self.remodelling_required = True
            return True
        elif evt == "down":
            if self.model.hasitem(self.selected_index + 1):
                self.is_selected_focused = False
                self.selected_index += 1
                self.remodelling_required = True
            return True
        elif evt == "up":
            if self.selected_index >= 1:
                self.is_selected_focused = False
                self.selected_index -= 1
                self.remodelling_required = True
            return True
        elif evt == "left" and self.scrolled_offset < 0:
            self.scrolled_offset += 1
            self.remodelling_required = True
            return True
        elif evt == "right":
            self.scrolled_offset -= 1
            self.remodelling_required = True
            return True
        elif evt == "home":
            if self.selected_index != 0:
                self.selected_index = 0
                self.remodelling_required = True
            return True
        elif evt == "end":
            # XXX how do we handle this?
            return True
        elif evt == "pagedown":
            for i in range(1, self.canvas.height):
                if not self.model.hasitem(self.selected_index + 1):
                    break
                self.selected_index += 1
                self.remodelling_required = True
            self.is_selected_focused = False
            return True
        elif evt == "pageup":
            if self.selected_index >= 1:
                self.selected_index = max(0, self.selected_index - self.canvas.height)
                self.is_selected_focused = False
                self.remodelling_required = True
            return True
        elif evt == "enter":
            if self.model.hasitem(self.selected_index):
                item = self.model.getitem(self.selected_index)
                if item.is_interactive():
                    self.is_selected_focused = True
                    #self.remodelling_required = True
            return True
        return False


def HListBox(model):
    return ListBox(ListBox.HORIZONTAL, model)

def VListBox(model):
    return ListBox(ListBox.VERTICAL, model)


class StubWidget(Widget):
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
    

#class ComboBox(Widget):
#    pass













