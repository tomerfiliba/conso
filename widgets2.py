import itertools
from terminal import Terminal
from events import KeyEvent, MouseEvent, ResizedEvent


class Widget(object):
    priority = 50
    def get_min_size(self):
        raise NotImplementedError()
    def get_desired_size(self):
        raise NotImplementedError()
    def render(self, canvas):
        raise NotImplementedError()
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
    __slots__ = ["text"]
    def __init__(self, text):
        self.text = text
    def get_min_size(self):
        return (min(6, len(self.text)), 1)
    def get_desired_size(self, parent_canvas):
        return (len(self.text), 1)
    def render(self, canvas):
        text = self.text
        if len(text) > canvas.width:
            text = text[:canvas.width - 3] + "..."
        canvas.write(text, 0, 0)

class ListBox(Widget):
    def __init__(self, model):
        self.model = model
        self.start_index = 0
        self.selected_index = 0
        self.hscrolled = 0
    def get_min_size(self):
        return (5, 3)
    def get_desired_size(self, parent_canvas):
        return (parent_canvas.width, parent_canvas.height)
    def render(self, canvas):
        canvas.draw_border()
        inner = canvas.subcanvas(3, 1, canvas.width - 3, canvas.height - 1)
        offy = 0
        for i in itertools.count(self.start_index):
            if not self.model.hasitem(i):
                break
            item = self.model.getitem(i)
            w, h = item.get_desired_size(inner)
            sc = inner.subcanvas(self.hscrolled, offy, w, h)
            item.render(sc)
            if self.selected_index == i:
                canvas.write(u"\u00bb", 1, 1 + offy)
            offy += h
            if offy >= inner.height - 1:
                break
    def on_key(self, evt):
        if self.model.hasitem(self.selected_index):
            curr = self.model.getitem(self.selected_index)
            if curr.on_event(evt):
                return True
        if evt.name == "up":
            self.select(self.selected_index - 1)
            return True
        elif evt.name == "down":
            self.select(self.selected_index + 1)
            return True
        elif evt.name == "pageup":
            self.select(self.selected_index - 10)
            return True
        elif evt.name == "pagedown":
            self.select(self.selected_index + 10)
            return True
    def select(self, index):
        if index < 0:
            index = 0
        if not self.model.hasitem(index):
            return
        self.selected_index = index
        self.start_index = index

class ListModel(object):
    def getitem(self, index):
        raise NotImplementedError()
    def hasitem(self, index):
        raise NotImplementedError()

class SimpleListModel(ListModel):
    def __init__(self, seq):
        self.seq = seq
    def hasitem(self, index):
        return index >= 0 and index < len(self.seq)
    def getitem(self, index):
        return Label(str(self.seq[index]))

class HLayout(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets
        self.focused = None
    def get_min_size(self):
        sizes = [w.get_min_size() for w in self.widgets]
        w = sum(s[0] for s in sizes)
        h = max(s[1] for s in sizes)
        return w, h
    def get_desired_size(self, parent_canvas):
        pass
    
    def _calc_widgets_size(self, total_size, axis):
        widgets = sorted(self.widgets, key = lambda w: w.priority)
        while True:
            output = []
            total_priorities = float(sum(w.priority for w in widgets))
            for i, wgt in enumerate(widgets):
                alloted = int(round(total_size * wgt.priority / total_priorities))
                min = wgt.get_min_size()[axis]
                if alloted < min:
                    del widgets[i]
                    break
                output.append((wgt, alloted))
            else:
                break
        return output[::-1]
    
    def render(self, canvas):
        offx = 0
        visible = self._calc_widgets_size(canvas.width, 0)
        self.visible_widgets = [w for w, s in visible]
        if not self.focused:
            self.focused = self.visible_widgets[0]

        for widget, width in visible:
            canvas2 = canvas.subcanvas(offx, 1, width, canvas.height - 1)
            if self.focused == widget:
                canvas.write(u"\u00b7", offx + canvas2.width / 2, 0)
            widget.render(canvas2)
            offx += canvas2.width
    
    def on_key(self, evt):
        if self.focused and self.focused.on_event(evt):
            return True
        if evt.name == "tab":
            if not self.visible_widgets:
                return False
            try:
                curr = self.visible_widgets.index(self.focused)
            except ValueError:
                self.focused = self.visible_widgets[0]
            else:
                self.focused = self.visible_widgets[(curr + 1) % len(self.visible_widgets)]
            return True

class Application(object):
    def __init__(self, root):
        self.root = root
    def main(self):
        with Terminal() as term:
            self._mainloop(term)
    
    def _mainloop(self, term):
        root_canvas = term.get_canvas()
        while True:
            self.root.render(root_canvas)
            evt = term.get_event()
            term.clear_screen()
            if evt == ResizedEvent:
                root_canvas = term.get_canvas()
            else:
                self.root.on_event(evt)


if __name__ == "__main__":
    m = SimpleListModel(["hi", "ther\ne", "world", "zolrf"] * 10)
    lb1 = ListBox(m)
    lb2 = ListBox(m)
    lb2.priority = 100
    root = HLayout(lb1, lb2)
    app = Application(root)
    app.main()






