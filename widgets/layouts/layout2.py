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
        pass
    def get_desired_size(self, pwidth, pheight):
        pass
    def render(self, style, focused = False, highlight = False):
        sw = self.get_selected_widget()
        for wgt, pos in self.visible_widgets:
            wgt.render(style, focused = focused and wgt is sw)

    def remodel(self, canvas = False):
        if not canvas:
            canvas = self.canvas
        
        self.canvas = canvas
    

    def select(self, index):
        pass
    
    def _on_key(self, evt):
        if evt == "esc":
            pass
        elif evt == "tab":
            pass
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








