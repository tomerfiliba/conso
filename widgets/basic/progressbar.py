from ..base import Widget


class ProgressBar(Widget):
    def __init__(self, percentage = 0, show_percentage = True):
        self.percentage = percentage
        self.show_percentage = show_percentage
    def get_min_size(self, pwidth, pheight):
        return (4, 1)
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, 1)
    def get_progress(self):
        return self.percentage
    def set_progress(self, percentage):
        if self.percentage < 0 or self.percentage > 100:
            raise ValueError("percentage must be in range 0..100")
        self.percentage = percentage
    def is_interactive(self):
        return False
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, style, focused = False, highlight = False):
        full = int((self.percentage * self.canvas.width) / 100)
        empty = self.canvas.width - full
        text = self.canvas.FULL_BLOCK * full + self.canvas.LIGHT_SHADE * empty
        if self.show_percentage and len(text) > 4:
            percentage = str(int(self.percentage))
            start = (len(text) - len(percentage)) // 2
            end = start + len(percentage)
            for i in range(len(text)):
                if start <= i < end:
                    if i < full:
                        self.canvas.write(i, 0, percentage[i - start], inversed = True)
                    else:
                        self.canvas.write(i, 0, percentage[i - start])
                else:
                    self.canvas.write(i, 0, text[i])
        else:
            self.canvas.write(0, 0, text)







