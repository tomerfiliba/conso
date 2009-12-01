from .base import Widget
import itertools


class LayoutInfo(object):
    __slots__ = ["widget", "alignment", "priority", "order"]
    def __init__(self, widget, alignment = "first", priority = 100):
        self.widget = widget
        self.alignment = alignment
        self.priority = priority
        self.order = self._counter.next()

class Layout(Widget):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, axis, widget_infos):
        self.axis = axis
        self.widget_infos = widget_infos
        self.visible_widgets = None
        self.selected_index = None
        self.is_selected_focused = True
    
    def get_min_size(self, pwidth, pheight):
        sizes = [wi.widget.get_min_size(pwidth, pheight) for wi in self.widget_infos]
        w = sum(s[self.axis] for s in sizes)
        h = max(s[1 - self.axis] for s in sizes)
        return w, h
    
    def get_desired_size(self, pwidth, pheight):
        if self.visible_widgets:
            return max(wgt[0].get_desired_size(pwidth, pheight) for wgt in self.visible_widgets)
        else:
            return (pwidth, pheight)
    
    def _calc_visible_widgets(self, canvas):
        if self.axis == self.HORIZONTAL:
            total_size = canvas.width
        else:
            total_size = canvas.height
        
        widget_infos = sorted(self.widget_infos, key = lambda wi: wi.priority)
        while True:
            output = []
            total_priorities = float(sum(wi.priority for wi in widget_infos))
            accumulated_size = 0
            for i, wi in enumerate(widget_infos):
                alloted = int(round(total_size * wi.priority / total_priorities))
                alloted = min(alloted, total_size - accumulated_size)
                min_size = wi.widget.get_min_size(canvas.width, canvas.height)[self.axis]
                max_size = wi.widget.get_desired_size(canvas.width, canvas.height)[self.axis]
                if alloted > max_size:
                    unused = alloted - max_size
                    total_size += unused
                    alloted -= unused

                accumulated_size += alloted
                assert accumulated_size <= total_size
                
                if alloted < min_size:
                    del widget_infos[i]
                    break
                output.append((wi.widget, alloted))
            else:
                break
        return output[::-1]
    
    def get_selected_widget(self):
        if not self.is_selected_focused:
            return None
        if self.selected_index < 0 or self.selected_index >= len(self.visible_widgets):
            return None
        return self.visible_widgets[self.selected_index][0]
    
    def remodel(self, canvas):
        self.visible_widgets = []
        self.canvas = canvas
        
        off = 0
        for wgt, alloted in self._calc_visible_widgets(canvas):
            if self.axis == self.HORIZONTAL:
                canvas2 = canvas.subcanvas(off, 0, alloted, canvas.height)
            else:
                canvas2 = canvas.subcanvas(0, off, canvas.width, alloted)
            
            wgt.remodel(canvas2)
            self.visible_widgets.append((wgt, canvas2.get_dims()))
            off += alloted
        
        if self.visible_widgets:
            self.selected_index = 0
        else:
            self.selected_index = None
    
    def render(self, style, focused = False, highlight = False):
        for i, (wgt, pos) in enumerate(self.visible_widgets):
            wgt.render(style, focused = focused and (i == self.selected_index), highlight = highlight)
    
    def _on_key(self, evt):
        sw = self.get_selected_widget()
        if sw and sw.on_event(evt):
            return True
        
        if self.axis == self.HORIZONTAL:
            next = "ctrl right"
            prev = "ctrl left"
        else:
            next = "ctrl down"
            prev = "ctrl up"
        
        if (evt == "tab" or evt == next) and self.selected_index <= len(self.visible_widgets) - 2:
            self.selected_index += 1
            self.is_selected_focused = True
            return True
        elif (evt == "shift tab" or evt == prev) and self.selected_index >= 1:
            self.selected_index -= 1
            self.is_selected_focused = True
            return True
        elif evt == "esc" and self.is_selected_focused:
            self.is_selected_focused = False
            return True
        return False

def _layout(widgets, axis):
    widgets2 = [wgt if isinstance(wgt, LayoutInfo) else LayoutInfo(wgt) 
        for wgt in widgets]
    counter = itertools.count()
    for wi in widgets2:
        wi.order = counter.next()
    return Layout(axis, widgets2)

def HLayout(*widgets):
    return _layout(widgets, Layout.HORIZONTAL)

def VLayout(*widgets):
    return _layout(widgets, Layout.VERTICAL)



