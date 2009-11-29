import inspect
from conso import widgets



def action(name, keys = (), doc = None):
    if isinstance(keys, basestring):
        keys = (keys,)
    def deco(func):
        doc2 = doc if doc else inspect.getdoc(func)
        if not doc2:
            doc2 = str(func)
        return ActionInfo(func, name, keys, doc)
    return deco
    
class ActionInfo(object):
    def __init__(self, func, name, keys, doc):
        self.func = func
        self.name = name
        self.keys = keys
        self.doc = doc

class Module(Widget):
    def __init__(self, root):
        self._root = root
        self._actions = self._get_actions()
        self._key_bindings = {}
        for act in self._actions:
            for key in act.keys:
                self._key_bindings[KeyEvent.from_string(key)] = act
        self.root = root
    
    @classmethod
    def _get_actions(cls):
        actions = []
        for name in dir(cls):
            obj = getattr(cls, name, None)
            if not isinstance(obj, ActionInfo):
                continue
            actions.append(obj)
        return actions
    
    def get_min_size(self, pwidth, pheight):
        return self.root.get_min_size(pwidth, pheight)
    def get_desired_size(self, pwidth, pheight):
        return self.root.get_desired_size(pwidth, pheight)
    def remodel(self, canvas):
        self.root.remodel(canvas)
    def render(self, style, focused = False, highlight = False):
        return self.root.render(style, focused = focused, highlight = highlight)
    
    @action("Help", keys = ["?"])
    def action_help(self):
        pass
    
    def on_event(self, evt):
        if self.root.on_event(evt):
            return True
        if evt in self._key_bindings:
            act = self._key_bindings[evt]
            return act.func(self)
        return False


class ListBoxModule(Module):
    def __init__(self, title, seq = ()):
        self.items = list(seq)
        actions = self._get_actions()
        root = Frame(title,
            VLayout(
                ListBox(SimpleListModel(self.items)),
                HLayout(Button(act.name) for act in actions),
            )
        )
        Module.__init__(self, root)
    
    @action("Del", keys = ["delete"])
    def action_del(self):
        pass
    
    # list API
    def __getitem__(self, index):
        return self.items[index]
    def __setitem__(self, index, value):
        self.items[index] = value
    def __delitem__(self, value):
        self.items[index] = value
    def insert(self, index, value):
        self.items.insert(index, value)
    def append(self, value):
        self.items.append(value)
    def pop(self, index = -1):
        return self.items.pop(index)























