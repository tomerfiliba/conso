from events import KeyEvent, MouseEvent


class Widget(object):
    __slots__ = ["priority", "canvas"]
    DEFAULT_PRIORITY = 500
    
    def __init__(self):
        self.priority = self.DEFAULT_PRIORITY
        self.canvas = None
    def is_interactive(self):
        pass
    def remodel(self, canvas):
        raise NotImplementedError()
    def render(self):
        pass
    def on_focus(self):
        self.focused = False
    def on_event(self, evt):
        if isinstance(evt, KeyEvent):
            return self.on_key(evt)
        elif isinstance(evt, MouseEvent):
            return self.on_mouse(evt)
        else:
            return False
    def on_key(self, key):
        return False
    def on_mouse(self, evt):
        return False

class Label(Widget):
    __slots__ = ["text", "attrs"]
    def __init__(self, text, attrs = None):
        Widget.__init__(self)
        self.text = text
        self.attrs = attrs
    def is_interactive(self):
        return False
    def remodel(self, canvas):
        self.canvas = canvas
    def get_min_size(self):
        return max(len(self.text), 4), 1
    def get_desired_size(self, pwidth, pheight):
        return len(self.text), 1
    def render(self):
        self.canvas.write(0, 0, self.text, self.attrs)

class TextEntry(Widget):
    pass

class TextBox(Widget):
    pass

class Button(Widget):
    pass

class ListBox(Widget):
    def __init__(self, model):
        self.model = model
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self):
        pass

class Layout(Widget):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, axis, widgets):
        Widget.__init__(self)
        self.axis = axis
        self.widgets = widgets
        self.focused_widget = None

    def get_min_size(self):
        sizes = [w.get_min_size() for w in self.widgets]
        w = sum(s[self.axis] for s in sizes)
        h = max(s[1 - self.axis] for s in sizes)
        return w, h
    
    def _calc_visible_widgets(self, total_size):
        widgets = sorted(self.widgets, key = lambda w: w.priority)
        while True:
            output = []
            total_priorities = float(sum(w.priority for w in widgets))
            accumulated_size = 0
            for i, wgt in enumerate(widgets):
                alloted = int(round(total_size * wgt.priority / total_priorities))
                alloted = min(alloted, total_size - accumulated_size)
                accumulated_size += alloted
                assert accumulated_size <= total_size
                min_size = wgt.get_min_size()[self.axis]
                if alloted < min_size:
                    del widgets[i]
                    break
                output.append((wgt, alloted))
            else:
                break
        return output[::-1]
    
    def remodel(self, canvas):
        self.visible_widgets = []
        if self.axis == self.HORIZONTAL:
            offx = 0
            for wgt, alloted in self._calc_visible_widgets(canvas.width):
                canvas2 = canvas.subcanvas(offx, 0, alloted, canvas.height)
                wgt.remodel(canvas2)
                self.visible_widgets.append((wgt, (offx, 0, canvas2.width, canvas2.height)))
                offx += alloted
        else:
            offy = 0
            for wgt, alloted in self._calc_visible_widgets(canvas.height):
                canvas2 = canvas.subcanvas(0, offy, canvas.width, alloted)
                wgt.remodel(canvas2)
                self.visible_widgets.append((wgt, (0, offy, canvas2.width, canvas2.height)))
                offy += alloted
        self.focused_widget = self.visible_widgets[0][0]
    
    def render(self):
        for wgt, pos in self.visible_widgets:
            wgt.render()

def HLayout(*widgets):
    return Layout(Layout.HORIZONTAL, widgets)

def VLayout(*widgets):
    return Layout(Layout.VERTICAL, widgets)

class TabbedLayout(Widget):
    pass











