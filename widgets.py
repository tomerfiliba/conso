class Widget(object):
    def get_sizes(self):
        raise NotImplementedError()
    def render(self, size):
        pass

class Label(Widget):
    def __init__(self, text):
        self.text = text
    def get_min_size(self):
        return (1, min(len(text), 6))
    def get_desired_size(self):
        return (1, len(text))
    def render(self, size, offset):
        pass

class HLayout(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets

class VLayout(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets
    def render(self):
        pass

class HScroll(Widget):
    def __init__(self, widgets):
        self.widgets = widgets
        self.selected = None

class VScroll(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets

class ListBox(Widget):
    def __init__(self, model):
        self.model = model
        self.selected = None
        self.first = 0
        self.count = 0
    def get_min_size(self):
        return (1, -1)
    def get_desired_size(self):
        return (-1, -1)

















