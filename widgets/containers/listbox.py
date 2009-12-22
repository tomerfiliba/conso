from ..base import Widget
from ..basic import Label


class ListModel(object):
    __slots__ = []
    def hasitem(self, index):
        raise NotImplementedError()
    def getitem(self, index):
        raise NotImplementedError()

class SimpleListModel(ListModel):
    __slots__ = ["list"]
    def __init__(self, seq):
        self.list = list(seq)
    def hasitem(self, index):
        return index >= 0 and index < len(self.list)
    def getitem(self, index):
        item = self.list[index]
        if not isinstance(item, Widget):
            item = Label(str(item))
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
    
    def __init__(self, axis, model, allow_scroll = False, auto_focus = False):
        assert isinstance(model, ListModel)
        self.axis = axis
        self.model = model
        self.start_index = 0
        self.last_index = None
        self.auto_focus = auto_focus
        self.selected_index = 0
        self.scrolled_offset = 0
        self.allow_scroll = allow_scroll
        self._is_selected_focused = False
        self.remodelling_required = True
    
    def _get_is_selected_focused(self):
        return self.auto_focus or self._is_selected_focused
    def _set_is_selected_focused(self, value):
        self._is_selected_focused = value
    is_selected_focused = property(_get_is_selected_focused, _set_is_selected_focused)
    
    def get_min_size(self, pwidth, pheight):
        return (5, 1)
    def get_desired_size(self, pwidth, pheight):
        if self.model.hasitem(self.start_index):
            item = self.model.getitem(self.start_index)
            dw, dh = item.get_desired_size(pwidth, pheight)
            if self.axis == self.VERTICAL:
                return (min(dw, pwidth), pheight)
            else:
                return (pwidth, min(dh, pheight))
        else:
            return self.get_min_size(pwidth, pheight)
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
                item.render(style, focused = focused and self.is_selected_focused, highlight = True)
            else:
                item.render(style)
            i += 1
            off += (dw + 1) if self.axis == self.HORIZONTAL else dh
        
        self.remodelling_required = False
    
    def _on_key(self, evt):
        if self.is_selected_focused:
            item = self.model.getitem(self.selected_index)
            if item.on_event(evt):
                return True
        
        if self.axis == self.HORIZONTAL:
            if evt == "right":
                evt = "down"
            elif evt == "left":
                evt = "up"
            elif evt == "up":
                evt = "left"
            elif evt == "down":
                evt = "right"
        
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
        elif evt == "left" and self.scrolled_offset < 0 and self.allow_scroll:
            self.scrolled_offset += 1
            self.remodelling_required = True
            return True
        elif evt == "right" and self.allow_scroll:
            self.scrolled_offset -= 1
            self.remodelling_required = True
            return True
        elif evt == "ctrl home" and self.allow_scroll:
            if self.scrolled_offset != 0:
                self.scrolled_offset = 0
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
            for i in range(0, self.canvas.height):
                if not self.model.hasitem(self.selected_index):
                    self.selected_index -= 1
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


def HListBox(model, **kwargs):
    return ListBox(ListBox.HORIZONTAL, model, **kwargs)

def VListBox(model, **kwargs):
    return ListBox(ListBox.VERTICAL, model, **kwargs)



