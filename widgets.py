class Widget(object):
    def get_sizes(self):
        raise NotImplementedError()
    def render(self, size):
        pass

class Label(Widget):
    def __init__(self, text):
        self.text = text
    def get_sizes(self):
        return (1, min(len(text), 6)), (1, len(text))
    def render(self, size):
        pass

class Textbox(Widget):
    pass

class Button(Widget):
    pass

class HLayout(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets

class VLayout(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets

class HScroll(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets

class VScroll(Widget):
    def __init__(self, *widgets):
        self.widgets = widgets


















