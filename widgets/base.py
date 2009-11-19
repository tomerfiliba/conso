from conso.events import KeyEvent, MouseEvent


class Widget(object):
    __slots__ = ["canvas"]
    
    def on_event(self, evt):
        if isinstance(evt, KeyEvent):
            return self._on_key(evt)
        elif isinstance(evt, MouseEvent):
            return self._on_mouse(evt)
        else:
            return False
    def _on_key(self, evt):
        return False
    def _on_mouse(self, evt):
        return False
    
    def get_priority(self):
        # XXX: remove this method
        return 500
    
    def is_interactive(self):
        return True
    def get_min_size(self, pwidth, pheight):
        raise NotImplementedError()
    def get_desired_size(self, pwidth, pheight):
        raise NotImplementedError()
    def remodel(self, canvas):
        raise NotImplementedError()
    def render(self, focused = False, highlight = False):
        raise NotImplementedError()


