import conso


def action(key):
    def deco(func):
        func._ui_action = dict(key = key)
        return func
    return deco



class Module(conso.Widget):
    def __init__(self):
        self._actions = set()
        self._triggers = {}
        for name in dir(self):
            obj = getattr(self.__class__, name, None)
            if not callable(obj) or not hasattr(obj, "_ui_action"):
                continue
            self._actions.add(obj)
            if obj._ui_action.get("key"):
                key = obj._ui_action["key"]
                evt = KeyEvent.from_string(key)
                if evt in self._triggers:
                    raise ValueError("key binding %r already defined" % (key,))
                self._triggers[evt] = obj
    
    def remodel(self, canvas):
        self.root = None
        self.root.remodel(canvas)
    
    def on_event(self, evt):
        if evt in self._triggers:
            func = self._triggers[evt]
            func(self)
            return True
        else:
            return self.root.on_event(evt)


if __name__ == "__main__":
    app = conso.Application(r)
    app.run()
