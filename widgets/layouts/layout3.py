from ..base import Widget

HORIZONTAL = 0
VERTICAL = 1


class LayoutInfo(object):
    LOW = 100
    NORMAL = 200
    HIGH = 300
    __slots__ = ["widget", "priority", "order"]
    
    def __init__(self, widget, priority = NORMAL):
        self.widget = widget
        self.priority = priority
        self.order = 0

class Fixed(LayoutInfo):
    __slots__ = ["size"]
    def __init__(self, widget, priority = LayoutInfo.NORMAL, size = None):
        LayoutInfo.__init__(self, widget, priority)
        self.size = size

    def get_bounds(self, canvas, remaining, axis):
        if axis == HORIZONTAL:
            total = canvas.width
        else:
            total = canvas.height
            width = canvas.width
            height = remaining
            
        if isinstance(self.size, float):
            size = int(min(max(0, round(self.size * total)), total))
        else:
            size = self.size
        
        minw, minh = self.widget.get_min_size(width, height)
        maxw, maxh = self.widget.get_desired_size(width, height)
        if minw > width or minh > height:
            return None
        
        if size is None:
            if axis == HORIZONTAL:
                size = minw
            else:
                size = minh
        
        return size, size

        #minw, minh = self.widget.get_min_size(canvas.width, remaining)
        #if wminw > canvas.width or wminh > remaining or wminh > minh:
        #    return -1
        #minh = max(minh, 0)
#        wmaxw, wmaxh = wi.widget.get_desired_size(canvas.width, remaining)
#        maxh = max(minh, min(maxh, wmaxh))
#        expansion = round((maxh - minh) * wi.priority / total_priorities)
#        alloted = min(int(minh + expansion), remaining)
#        return alloted


class Scaled(LayoutInfo):
    __slots__ = ["min", "max"]
    
    def __init__(self, widget, priority = LayoutInfo.NORMAL, min = 0, max = 1.0):
        LayoutInfo.__init__(self, widget, priority)
        self.min = min
        self.max = max

    def get_bounds(self, canvas, remaining, axis):
        if axis == HORIZONTAL:
            total = canvas.width
        else:
            total = canvas.height
            width = canvas.width
            height = remaining
        
        if isinstance(self.min, float):
            min2 = int(min(max(0, round(self.min * total)), total))
        else:
            min2 = self.min
        if isinstance(self.max, float):
            max2 = int(min(max(0, round(self.max * total)), total))
        else:
            max2 = self.max
        
        minw, minh = self.widget.get_min_size(width, height)
        maxw, maxh = self.widget.get_desired_size(width, height)
        if minw > width or minh > height:
            return None
        
        if size is None:
            if axis == HORIZONTAL:
                size = minw
            else:
                size = minh
        
        return size, size

class Layout(Widget):
    def __init__(self, widget_infos, axis):
        self.axis = axis
        self.widget_infos = widget_infos
        self.visible_widgets = ()
        self._visible_to_index = {}
        self.selected_index = -1
        self.is_selected_focused = False
    
    def _allocate_vertical(self, wi, canvas, remaining, total_priorities):
        minh, maxh = wi.get_range(canvas, remaining, self.axis)

        #wminw, wminh = wi.widget.get_min_size(canvas.width, remaining)
        #if wminw > canvas.width or wminh > remaining or wminh > minh:
        #    return -1
        #wmaxw, wmaxh = wi.widget.get_desired_size(canvas.width, remaining)
        #maxh = max(minh, min(maxh, wmaxh))
        
        expansion = round((maxh - minh) * wi.priority / total_priorities)
        alloted = min(int(minh + expansion), remaining)
        return alloted
    
#    def _allocate_horizontal(self, wi, canvas, remaining, total_priorities):
#        if isinstance(wi.min, float):
#            minw = max(min(0, round(wi.min * canvas.width)), canvas.width)
#        else:
#            minw = wi.min
#        wminw, wminh = wi.widget.get_min_size(canvas.width, remaining)
#        if wminw > canvas.width or wminh > remaining or wminh > minh:
#            return -1
#        minh = max(minh, 0)
#        if isinstance(wi.max, float):
#            maxh = max(min(0, round(wi.max * canvas.height)), canvas.height)
#        else:
#            maxh = wi.max
#        wmaxw, wmaxh = wi.widget.get_desired_size(canvas.width, remaining)
#        maxh = max(minh, min(maxh, wmaxh))
#        expansion = round((maxh - minh) * wi.priority / total_priorities)
#        alloted = min(int(minh + expansion), remaining)
#        return alloted
    
    def _allocate_space(self, wi, canvas, remaining, total_priorities):
        if self.axis == VERTICAL:
            return self._allocate_vertical(wi, canvas, remaining, total_priorities)
        else:
            return self._allocate_horizontal(wi, canvas, remaining, total_priorities)
    
    def _calc_visible_widgets(self, canvas):
        infos = sorted(self.widget_infos, key = lambda wi: wi.priority, reverse = True)
        fixed = [wi for wi in infos if isinstance(wi, Fixed)]
        scaled = [wi for wi in infos if isinstance(wi, Scaled)]
        scaled_priorities = sum(wi.priority for wi in scaled)
        
        finished = False
        while not finished:
            visible = []
            remaining = canvas.height
            fixed_priorities = sum(wi.priority for wi in fixed)
            total_priorities = float(fixed_priorities + scaled_priorities) 
            for i, wi in enumerate(fixed):
                alloted = self._allocate_space(wi, canvas, remaining, total_priorities)
                if alloted < 0:
                    del fixed[i]
                    break
                assert remaining >= alloted
                remaining -= alloted
                visible.append((wi.order, wi.widget, alloted))
                if remaining <= 0:
                    finished = True
                    break
            else:
                finished = True
        
        for wi in scaled:
            if remaining <= 0:
                break
            alloted = self._allocate_space(wi, canvas, remaining, total_priorities)
            if alloted < 0:
                continue
            visible.append((wi.order, wi.widget, alloted))

        visible.sort(key = lambda seq: seq[0])
        return [(widget, alloted) for order, widget, alloted in visible]
    
    def remodel(self, canvas):
        if canvas is None:
            canvas = self.canvas
        if canvas is None:
            raise ValueError("canvas not set")
        self.canvas = canvas
        if 0 <= self.selected_index < len(self.visible_widgets):
            old = self.visible_widgets[self.selected_index]
        else:
            self.selected_index = -1
            old = NotImplemented
        self.visible_widgets = []
        self._visible_to_index.clear()
        visible = self._calc_visible_widgets(canvas)
        start = 0
        for i, (widget, alloted) in enumerate(visible):
            if widget == old:
                self.selected_index = i
            if self.axis == VERTICAL:
                canvas2 = canvas.subcanvas(0, start, canvas.width, alloted)
            else:
                canvas2 = canvas.subcanvas(start, 0, alloted, canvas.height)
            widget.remodel(canvas2)
            self.visible_widgets.append((widget, (canvas2.offx, canvas2.offy, canvas2.width, canvas2.height)))
            self._visible_to_index[widget] = i
            start += alloted

        if self.selected_index < 0 and self.visible_widgets:
            self._select_first_interactive(range(0, len(self.visible_widgets)))
    
    def render(self, style, focused = False, highlight = False):
        sw = self.get_selected_widget()
        for i, (wgt, bounds) in enumerate(self.visible_widgets):
            wgt.render(style, focused = (focused and wgt == sw), highlight = highlight)
    
    def get_selected_widget(self):
        if self.selected_index >= len(self.visible_widgets):
            self.selected_index = -1
        if self.selected_index < 0 or not self.is_selected_focused:
            return None
        return self.visible_widgets[self.selected_index][0]

    def _select(self, index):
        if index is None:
            self.selected_index = -1
            self.is_selected_focused = False
        elif 0 <= index < len(self.visible_widgets):
            self.selected_index = index
            self.is_selected_focused = True
        else:
            raise IndexError("index out of range")
    
    def select(self, widget):
        index = None if widget is None else self._visible_to_index[widget]
        self._select(index)
    
    def _select_first_interactive(self, range):
        for i in range:
            widget = self.visible_widgets[i][0]
            if widget.is_interactive():
                self._select(i)
                return True
        return False
    
    def _on_key(self, evt):
        sw = self.get_selected_widget()
        if sw and sw.on_event(evt):
            return True
        
        if evt == "esc" and sw:
            self.is_selected_focused = False
            return True
        elif evt == "tab" and 0 <= self.selected_index < len(self.visible_widgets):
            return self._select_first_interactive(range(self.selected_index + 1, len(self.visible_widgets)))
        elif evt == "shift tab" and 0 <= self.selected_index < len(self.visible_widgets):
            return self._select_first_interactive(range(self.selected_index - 1, 0, -1))
        return False

    def _on_mouse(self, evt):
        for wgt, (x, y, w, h) in self.visible_widgets:
            if x <= evt.x < x + w and y <= evt.y < y + h:
                evt.x -= x
                evt.y -= y
                #if evt.btn == evt.BTN_RELEASE:
                self.select(wgt)
                wgt.on_event(evt)
                return True
        return False


def _layout(widgets, axis):
    widgets2 = [wgt if isinstance(wgt, LayoutInfo) else Scaled(wgt) 
        for wgt in widgets]
    for i, wi in enumerate(widgets2):
        wi.order = i
    return Layout(widgets2, axis)

def HLayout(*widgets):
    return _layout(widgets, HORIZONTAL)

def VLayout(*widgets):
    return _layout(widgets, VERTICAL)










