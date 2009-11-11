import itertools
from terminal import Terminal, Resized


class Widget(object):
    def get_min_size(self):
        raise NotImplementedError()
    def get_desired_size(self):
        raise NotImplementedError()
    def render(self, canvas):
        raise NotImplementedError()
    def on_event(self, evt):
        pass

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
    def on_event(self, evt):
        if evt.name == "up":
            self.select(self.selected_index - 1)
        elif evt.name == "down":
            self.select(self.selected_index + 1)
        elif evt.name == "pageup":
            self.select(self.selected_index - 10)
        elif evt.name == "pagedown":
            self.select(self.selected_index + 10)
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
        self.focused = widgets[0]
    def get_min_size(self):
        sizes = [w.get_min_size() for w in self.widgets]
        w = sum(s[0] for s in sizes)
        h = max(s[1] for s in sizes)
        return w, h
    def get_desired_size(self, parent_canvas):
        pass
    def render(self, canvas):
        per_item_width = canvas.width / len(self.widgets)
        offx = 0
        for w in self.widgets:
            canvas2 = canvas.subcanvas(offx, 0, per_item_width, canvas.height)
            w.render(canvas2)
    def on_event(self, evt):
        self.focused.on_event(evt)


class Application(object):
    def __init__(self, root):
        self.root = root
    def main(self):
        with Terminal() as term:
            try:
                self._mainloop(term)
            except KeyboardInterrupt:
                pass
    
    def _mainloop(self, term):
        while True:
            root_canvas = term.get_canvas()
            term.clear_screen()
            self.root.render(root_canvas)
            evt = term.get_event()
            if evt == Resized:
                pass
            else:
                self.root.on_event(evt)


if __name__ == "__main__":
    m = SimpleListModel(["hi", "ther\ne", "world", "zolrf"] * 10)
    lb1 = ListBox(m)
    lb2 = ListBox(m)
    root = HLayout(lb1, lb2)
    app = Application(root)
    app.main()






