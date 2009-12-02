import inspect
from .base import Widget


class ActionInfo(object):
    def __init__(self, func, title = None, doc = None, keys = ()):
        if not doc:
            doc = inspect.getdoc(func)
            if not doc:
                doc = str(func)
        if isinstance(keys, basestring):
            keys = (keys,)
        self.func = func
        self.title = title
        self.doc = doc
        self.keys = keys
    
    def __get__(self, obj, cls):
        if not obj:
            return self
        else:
            return lambda: self.func(obj)
    
    def __call__(self, obj):
        return self.func(obj)


def action(title = None, **kwargs):
    def deco(func):
        return ActionInfo(func, title, **kwargs)
    return deco

class Module(Widget):
    def __init__(self, root):
        self.root = root
        self._actions = self._get_actions()
        self._key_bindings = {}
        for act in self._actions:
            for key in act.keys:
                self._key_bindings[KeyEvent.from_string(key)] = act
    
    @classmethod
    def _get_actions(cls):
        actions = []
        for name in dir(cls):
            obj = getattr(cls, name, None)
            if not isinstance(obj, ActionInfo):
                continue
            actions.append(obj)
        return actions

    def is_interactive(self):
        return self.root.is_interactive()
    def get_min_size(self, pwidth, pheight):
        return self.root.get_min_size(pwidth, pheight)
    def get_desired_size(self, pwidth, pheight):
        return self.root.get_desired_size(pwidth, pheight)
    def remodel(self, canvas):
        self.root.remodel(canvas)
    def render(self, style, focused = False, highlight = False):
        return self.root.render(style, focused = focused, highlight = highlight)
    
    def on_event(self, evt):
        if self.root.on_event(evt):
            return True
        if evt in self._key_bindings:
            act = self._key_bindings[evt]
            return act.func(self)
        return False

class SimpleModule(Module):
    def __init__(self, body, header = None):
        self.body = body
        self.banner = StubWidget()
        self.header = header if header else StubWidget()
        self.footer = StubWidget()
        Module.__init__(self, 
            VLayout(
                self.header,
                self.body,
                self.banner,
                self.footer,
            )
        )
    
    def _get_help_message(self):
        pass
    
    def _get_footer_line(self):
        pass
    
    @action("Help", keys = ["?"])
    def action_help(self):
        self.banner.set(LabelBox(self._get_help_message()))
        return True

    @action(keys = ["esc"])
    def action_clear_banner(self):
        if self.banner.is_set():
            self.banner.clear()
            return True
        return False


class ListBoxModule(SimpleModule):
    def __init__(self, items = ()):
        self.items = list(items)
        SimpleModule.__init__(self, ListBox(SimpleListModel(self.items)))

    @action(title = "Delete", keys = ["delete"])
    def action_delete_selected(self):
        if self.listbox.get_selected_widget():
            del self.items[self.listbox.selected_index]
            return True
        return False























