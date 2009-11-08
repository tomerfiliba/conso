class Widget(object):
    def get_min_size(self):
        return (1, 1)
    def get_desired_size(self):
        return (-1, -1)
    def render(self, size, offset):
        pass


class Label(Widget):
    def __init__(self, text):
        self.text = text
    def get_min_size(self):
        return (1, min(len(self.text), 6))
    def get_desired_size(self):
        return (1, len(self.text))
    def render(self, size, offset):
        off_x, off_y = offset
        display_text = self.text[off_x:off_x+size]
        return Text(0, 0, display_text)













