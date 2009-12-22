from ..base import Widget


class LayoutInfo(object):
    def __init__(self, widget, priority = 10, scaled = True):
        self.widget = widget
        self.priority = priority
        self.scaled = scaled


class Layout(Widget):
    def __init__(self, layout_infos):
        self.layout_infos = layout_infos
        self.visible_widgets = []
        self.selected_index = -1
    
    def get_min_size(self, pwidth, pheight):
        sw = self.get_selected_widget()
        if not sw:
            return (0, 0)
        else:
            return sw.get_min_size(pwidth, pheight)
    def get_desired_size(self, pwidth, pheight):
        pass
    
    def render(self, style, focused = False, highlight = False):
        sw = self.get_selected_widget()
        for wgt, pos in self.visible_widgets:
            wgt.render(style, focused = focused and wgt is sw)

    def _calc_visible_widgets(self):
        output = []
        
        for info in sorted(self.layout_infos, key = lambda info: info.priority):
            minw, minh = info.get_min_size(self.canvas.width, self.canvas.height)
            maxw, maxh = info.get_desired_size(self.canvas.width, self.canvas.height)
        
        
        for info in self.layout_infos:
            pass
    
    def remodel(self, canvas = False):
        if not canvas:
            canvas = self.canvas
        
        self.canvas = canvas
        self.visible_widgets = self._calc_visible_widgets()
    
    def get_selected_widget(self):
        if self.selected_index >= len(self.visible_widgets):
            self.selected_index = -1
        if self.selected_index < 0:
            return None
        return self.visible_widgets[self.selected_index][0]

    def select(self, index):
        pass
    
    def _on_key(self, evt):
        sw = self.get_selected_widget()
        if sw and sw.on_event(evt):
            return True
        
        if evt == "esc" and sw:
            pass
        elif evt == "tab":
            if self.selected_index < 0 and self.visible_widgets:
                self.selected_index = 0
            #if self.selected_index <= self.visible_widgets:
            #    self.selected_index = 0
            
        elif evt == "shift tab":
            pass
    
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








