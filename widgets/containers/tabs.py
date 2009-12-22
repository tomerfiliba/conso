from ..base import Widget


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


