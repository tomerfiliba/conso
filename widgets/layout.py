from .base import Widget


class Layout(Widget):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, axis, widgets):
        self.axis = axis
        self.widgets = widgets
        self.visible_widgets = None
        self.selected_index = None
        self.is_selected_focused = True
    
    def get_min_size(self, pwidth, pheight):
        sizes = [w.get_min_size(pwidth, pheight) for w in self.widgets]
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
        
        widgets = sorted(self.widgets, key = lambda w: w.get_priority())
        while True:
            output = []
            total_priorities = float(sum(w.get_priority() for w in widgets))
            accumulated_size = 0
            for i, wgt in enumerate(widgets):
                alloted = int(round(total_size * wgt.get_priority() / total_priorities))
                alloted = min(alloted, total_size - accumulated_size)
                accumulated_size += alloted
                assert accumulated_size <= total_size
                min_size = wgt.get_min_size(canvas.width, canvas.height)[self.axis]
                max_size = wgt.get_desired_size(canvas.width, canvas.height)[self.axis]
                if alloted > max_size:
                    alloted = max_size
                if alloted < min_size:
                    del widgets[i]
                    break
                output.append((wgt, alloted))
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
        visible_set = set()
        if self.axis == self.HORIZONTAL:
            offx = 0
            for wgt, alloted in self._calc_visible_widgets(canvas):
                canvas2 = canvas.subcanvas(offx, 0, alloted, canvas.height)
                wgt.remodel(canvas2)
                self.visible_widgets.append((wgt, (offx, 0, canvas2.width, canvas2.height)))
                visible_set.add(wgt)
                offx += alloted
        else:
            offy = 0
            for wgt, alloted in self._calc_visible_widgets(canvas):
                canvas2 = canvas.subcanvas(0, offy, canvas.width, alloted)
                wgt.remodel(canvas2)
                self.visible_widgets.append((wgt, (0, offy, canvas2.width, canvas2.height)))
                visible_set.add(wgt)
                offy += alloted
        
        self.selected_index = 0
    
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

def HLayout(*widgets):
    return Layout(Layout.HORIZONTAL, widgets)

def VLayout(*widgets):
    return Layout(Layout.VERTICAL, widgets)



