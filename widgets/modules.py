import itertools
import inspect
from ..events import KeyEvent
from .base import Widget
from .basic import Button, LabelBox
from .containers import StubBox, Frame
from .containers import SimpleListModel, HListBox, VListBox
from .layouts import VLayout, HLayout


class ActionInfo(object):
    _counter = itertools.count()
    
    def __init__(self, func, title, doc, keys):
        self.title = title
        self.doc = doc
        self.keys = keys
        self.func = func
        self.order = self._counter.next()

def action(title = None, doc = None, keys = ()):
    def deco(func):
        doc2 = doc
        if not doc2:
            doc2 = inspect.getdoc(func)
        if not doc2:
            doc2 = str(func)
        return ActionInfo(func, title, doc2, keys)
    return deco


class Module(Widget):
    def __init__(self, root):
        self.root = root
        self._actions = self._get_actions()
        self._key_bindings = {}
        for action in self._actions:
            for key in action.keys:
                self._key_bindings[KeyEvent.from_string(key)] = action
    
    def _get_actions(self):
        actions = []
        for name in dir(self.__class__):
            obj = getattr(self.__class__, name)
            if isinstance(obj, ActionInfo):
                actions.append(obj)
        actions.sort(key = lambda action: action.order)
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
        self.root.render(style, focused = focused, highlight = highlight)
    def on_event(self, evt):
        if self.root.on_event(evt):
            return True
        if evt in self._key_bindings:
            action = self._key_bindings[evt]
            return action.func(self, evt)
        return False

class FramedModule(Module):
    def __init__(self, body, header = None):
        self.body = body
        self.header = StubBox(header)
        footer_actions = SimpleListModel([])
        self.footer = HListBox(footer_actions, auto_focus = True)
        self.banner = StubBox()
        Module.__init__(self, 
            VLayout(
                self.body,
                self.header,
                self.banner,
                self.footer
            )
        )
        self._populate_footer(footer_actions)
    
    def _populate_footer(self, footer_actions):
        for act in self._actions:
            if act.title:
                btn = Button(act.title, lambda inst, func = act.func: func(self, None))
                footer_actions.append(btn)
    
    def _set_banner(self, widget):
        self.banner.unset()
        self.banner.set(widget)
        self.root.remodel()
        self.root.selected_index = 2
    
    def _hide_banner(self):
        self.banner.unset()
        self.root.remodel()
        self.root.selected_index = 1
    
    def _get_help_message(self):
        lines = []
        doc = inspect.getdoc(self)
        if doc:
            lines.extend(doc.splitlines())
            lines.append("")
        
        for action in self._actions:
            lines.append(" * %s [%s]: %s" % (action.title, ", ".join(action.keys), action.doc))
        lines.sort()
        return lines * 10
    
    @action(title = "Help", keys = ["?"])
    def action_help(self, evt):
        """Display this help message, describing the different commands and key bindings"""
        self._set_banner(Frame(LabelBox(self._get_help_message()), "Help"))
        return True
    
    @action(keys = ["esc"])
    def action_unfocus(self, evt):
        if self.banner.is_set():
            self._hide_banner()
            return True
        return False


class ListModule(FramedModule):
    def __init__(self, items = (), title = None):
        if title is None:
            title = self.__class__.__name__
            if title.lower().endswith("module"):
                title = title[:-6]
        self.model = SimpleListModel(items)
        self.vlist = VListBox(self.model)
        FramedModule.__init__(self, Frame(self.vlist, title = title))
    
    def append(self, item):
        self.model.append(item)
    def insert(self, index, item):
        self.model.insert(index, item)
    def pop(self, index = -1):
        self.model.pop(index)
    def __getitem__(self, index):
        return self.model[index]
    def __delitem__(self, index):
        del self.model[index]
    def __setitem__(self, index, value):
        self.model[index] = value
    
    def get_selected_index(self):
        if self.model.hasitem(self.vlist.selected_index):
            return self.vlist.selected_index
        else:
            return -1
    
    def set_selected_index(self, index):
        if index < 0:
            index = 0
        if self.model.hasitem(index):
            self.vlist.selected_index = index
        else:
            pass
    
    @action("Delete", keys = ["del"])
    def action_delete_selected(self, evt):
        index = self.get_selected_index()
        if index >= 0:
            del self[index]
        if not self.model.hasitem(index) and index >= 1:
            self.set_selected_index(index - 1)
        return True





