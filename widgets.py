class Widget(object):
    def get_min_size(self):
        return (1, 1)
    def get_desired_size(self):
        return (-1, -1)
    def render(self, size, offset):
        raise NotImplementedError()





