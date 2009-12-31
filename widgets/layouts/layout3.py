from ..base import Widget


class LayoutInfo(object):
    LOW = 100
    NORMAL = 200
    HIGH = 300
    __slots__ = ["widget", "priority", "min", "max", "order"]
    
    def __init__(self, widget, priority = NORMAL, min = 0, max = None):
        self.widget = widget
        self.priority = priority
        self.min = min
        self.max = max
        self.order = 0

class Fixed(LayoutInfo):
    __slots__ = []
    def __init__(self, widget, priority = LayoutInfo.NORMAL, size = None):
        LayoutInfo.__init__(self, widget, priority, min = size, max = size)

class Scaled(LayoutInfo):
    __slots__ = []

class Layout(Widget):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, widget_infos, axis):
        self.axis = axis
        self.widget_infos = widget_infos
        self.visible_widgets = ()
        self.selected_index = -1
        self.is_selected_focused = False
    
    def _allocate_vertical(self, wi, canvas, remaining):
        if isinstance(wi.min, float):
            minh = max(min(0, round(wi.min * canvas.height)), canvas.height)
        else:
            minh = wi.min
        wminw, wminh = wi.widget.get_min_size(canvas.width, remaining)
        if wminw < canvas.width or wminh < remaining:
            return -1
        minh = min(max(minh, wminh), 0)
        if isinstance(wi.max, float):
            maxh = max(min(0, round(wi.max * canvas.height)), canvas.height)
        else:
            maxh = wi.max
        wmaxw, wmaxh = wi.widget.get_desired_size(canvas.width, remaining)
        maxh = max(minh, min(maxh, wmaxh))
        expansion = round((maxh - minh) * wi.priority / total_priorities)
        alloted = max(minh + expansion, remaining)
        return alloted
    
    def _allocate_horizontal(self, wi, canvas, remaining):
        if isinstance(wi.min, float):
            minw = max(min(0, round(wi.min * canvas.width)), canvas.width)
        else:
            minw = wi.min
        wminw, wminh = wi.widget.get_min_size(remaining, canvas.height)
        if wminw < remaining or wminh < canvas.height:
            return -1
        minw = min(max(minw, wminw), 0)
        if isinstance(wi.max, float):
            maxw = max(min(0, round(wi.max * canvas.width)), canvas.width)
        else:
            maxw = wi.max
        wmaxw, wmaxh = wi.widget.get_desired_size(remaining, canvas.height)
        maxw = max(minw, min(maxw, wmaxw))
        expansion = round((maxw - minw) * wi.priority / total_priorities)
        alloted = max(minw + expansion, remaining)
        return alloted
    
    def _allocate_space(self, wi, canvas, remaining):
        if self.axis == self.VERTICAL:
            return self._allocate_vertical(wi, canvas, remaining)
        else:
            return self._allocate_horizontal(wi, canvas, remaining)
    
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
                alloted = self._allocate_space(wi, canvas, remaining)
                if alloted < 0:
                    del fixed[i]
                    break
                assert remaining >= alloted
                remaining -= alloted
                visible.append((wi.order, wi.widget, alloted))
                if remaining <= 0:
                    finished = True
                    break
        
        for wi in scaled:
            if remaining <= 0:
                break
            alloted = self._allocate_space(wi, canvas, remaining)
            if alloted < 0:
                continue
            visible.append((wi.order, wi.widget, alloted))
        
        visible.sort(key = lambda seq: seq[0])
        return [(widget, alloted) for order, widget, alloted in visible]
    
    def remodel(self, canvas):
        if canvas is None:
            canvas = self.canvas
        assert canvas is not None
        self.canvas = canvas
        if 0 <= self.selected_index < len(self.visible_widgets):
            old = self.visible_widgets[self.selected_index]
        else:
            self.selected_index = -1
            old = None
        self.visible_widgets = []
        visible = self._calc_visible_widgets(canvas)
        start = 0
        for i, (widget, alloted) in enumerate(visible):
            if widget == old:
                self.selected_index = i
            if self.axis == self.VERTICAL:
                canvas2 = canvas.subcanvas(0, start, canvas.width, alloted)
            else:
                canvas2 = canvas.subcanvas(start, 0, alloted, canvas.height)
            widget.remodel(canvas2)
            self.visible_widgets.append((widget, (canvas2.offx, canvas2.offy, canvas2.width, canvas2.height)))
            start += alloted
        
        if self.selected_index < 0 and self.visible_widgets:
            self.selected_index = 0
            self.is_selected_focused = False
    
    def render(self, style, focused = False, highlight = False):
        for i, (wgt, bounds) in enumerate(self.visible_widgets):
            wgt.render(style, focused = focused and (i == self.selected_index), highlight = highlight)
    
    def get_selected_widget(self):
        if self.selected_index >= len(self.visible_widgets):
            self.selected_index = -1
        if self.selected_index < 0 or not self.is_selected_focused:
            return None
        return self.visible_widgets[self.selected_index][0]

    def _on_key(self, evt):
        sw = self.get_selected_widget()
        if sw and sw.on_event(evt):
            return True
        
        assert self.visible_widgets
        if evt == "esc" and sw:
            self.is_selected_focused = False
            return True
        elif evt == "tab" and self.selected_index >= 0:
            for i in range(self.selected_index + 1, len(self.visible_widgets) - 2):
                widget = self.visible_widgets[i][0]
                if widget.is_interactive():
                    self.selected_index = i
                    self.is_selected_focused = True
                    return True
        elif evt == "shift tab" and self.selected_index >= 0:
            for i in range(self.selected_index - 1, 0, -1):
                widget = self.visible_widgets[i][0]
                if widget.is_interactive():
                    self.selected_index = i
                    self.is_selected_focused = True
                    return True
        return False
    
    def _on_mouse(self, evt):
        for wgt, (x, y, w, h) in self.visible_widgets:
            if x <= evt.x <= x + w and y <= evt.y <= y + h:
                evt.x -= x
                evt.y -= y
                if evt.btn == evt.BTN_RELEASE:
                    self.select(wgt)
                    handled = True
                if wgt.on_event(evt):
                    handled = True
                return handled
        return False


def _layout(widgets, axis):
    widgets2 = [wgt if isinstance(wgt, LayoutInfo) else Scaled(wgt) 
        for wgt in widgets]
    for i, wi in enumerate(widgets2):
        wi.order = i
    return Layout(widgets2, axis)

def HLayout(*widgets):
    return _layout(widgets, Layout.HORIZONTAL)

def VLayout(*widgets):
    return _layout(widgets, Layout.VERTICAL)










