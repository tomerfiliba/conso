import sys
import inspect
from terminal import Terminal
from events import KeyEvent, MouseEvent, ResizedEvent


class SwitchParsingError(Exception):
    pass
class TailArgsError(SwitchParsingError):
    pass
class DanglingArgsError(TailArgsError):
    pass
class ParameterTypeError(SwitchParsingError):
    pass
class MissingParameterError(SwitchParsingError):
    pass
class InvalidSwitchError(SwitchParsingError):
    pass
class RequiredSwitchNotGiven(SwitchParsingError):
    pass
class SwitchGivenMoreThanOnce(SwitchParsingError):
    pass


def switch(names, type = None, doc = None, multiple = False, required = False, overriding = False):
    if isinstance(names, basestring):
        names = [names]
    if not names:
        raise ValueError("at least one name must be given to a CLI switch")
    for n in names:
        if not n:
            raise ValueError("name cannot be empty")
    def deco(func):
        doc2 = doc
        if not doc:
            doc2 = inspect.getdoc(func)
        if not doc2:
            doc2 = repr(func)
        if type:
            a, va, kw, dfl = inspect.getargspec(func)
            if len(a) - 1 + bool(va) < 0:
                raise TypeError("switches taking a parameter must accept at least one positional argument")
        func._switch_info = dict(names = names, type = type, doc = doc2, multiple = multiple, 
            required = required, invoked = False)
        return func
    return deco


class CliApplication(object):
    SHORT_SWITCH_PREFIX = "-"
    LONG_SWITCH_PREFIX = "--"
    END_OF_SWITCHES = "--"
    
    def __init__(self):
        self._prepare_switches()

    def _prepare_switches(self):
        self._switches = {}
        for name in dir(self):
            obj = getattr(self, name)
            if not hasattr(obj, "_switch_info"):
                continue
            swinfo = obj._switch_info
            for key in swinfo["names"]:
                if key in self._switches and not swinfo["overriding"]:
                    raise ValueError("multiple switches register the same name: %r" % (name,))
                self._switches[key] = (obj, swinfo)
    
    def _parse_cli_args(self, argv):
        tail = []
        while argv:
            arg = argv.pop(0)
            param = None
            if arg == self.END_OF_SWITCHES:
                if tail:
                    raise DanglingArgsError("dangling arguments appear before %r: %r" % (arg, tail))
                return argv
            elif arg.startswith(self.LONG_SWITCH_PREFIX):
                if tail:
                    raise DanglingArgsError("dangling arguments appear before %r: %r" % (arg, tail))
                self._invoke_switch(arg[len(self.LONG_SWITCH_PREFIX):], argv)
            elif arg.startswith(self.SHORT_SWITCH_PREFIX):
                if tail:
                    raise DanglingArgsError("dangling arguments appear before %r: %r" % (arg, tail))
                arg = arg[len(self.SHORT_SWITCH_PREFIX):]
                if len(arg) > 1:
                    arg = arg[0]
                    rest = arg[1:]
                    argv.insert(0, self.SHORT_SWITCH_PREFIX + rest)
                self._invoke_switch(arg, argv)
            else:
                tail.append(arg)
        
        for swobj, swinfo in self._switches.itervalues():
            if swinfo["required"] and not swinfo["invoked"]:
                raise RequiredSwitchNotGiven("%r is required" % (swinfo["names"][0],))
        
        return tail
    
    def _invoke_switch(self, sw, argv):
        if sw not in self._switches:
            raise InvalidSwitchError(sw)
        swobj, swinfo = self._switches[sw]
        if swinfo["invoked"] and not swinfo["multiple"]:
            raise SwitchGivenMoreThanOnce("switch %r (or an alias) given more than once" % (sw,))
        swinfo["invoked"] = True
        if swinfo["type"]:
            if not argv:
                raise MissingParameterError("expected a parameter to follow %r" % (sw,))
            param = argv.pop(0)
            try:
                param = swinfo["type"](param)
            except (TypeError, ValueError), ex:
                raise ParameterTypeError("invalid parameter type for %r; expected %r" % (sw, swinfo["type"]))
            swobj(param)
        else:
            swobj()

    def _parse_short_switch(self, sw, argv):
        if len(arg) > 1:
            arg = arg[0]
            rest = arg[1:]
            swobj, swinfo = self._switches[arg]
            if swinfo["type"]:
                param = swinfo["type"](rest)
                swobj(rest)
            else:
                argv.insert(0, self.SHORT_SWITCH_PREFIX + rest)
                swobj()
        else:
            swobj, swinfo = self._switches[arg]
            if swinfo["type"]:
                param = swinfo["type"](rest)
                swobj(param)
            else:
                swobj()
    
    def run(self, argv = None, exit = True):
        if not argv:
            argv = sys.argv
        exe = argv[0]
        args = argv[1:]
        
        try:
            tail = self._parse_cli_args(args)
            a, va, kw, dfl = inspect.getargspec(self.main)
            if not va:
                atmost = len(a) - 1
                atleast = atmost - len(dfl)
                if len(tail) > atmost:
                    raise TailArgsError("application takes at most %d positional arguments, %d given" % (atmost, len(tail)))
                if len(tail) < atleast:
                    raise TailArgsError("application takes at least %d positional arguments, %d given" % (atleast, len(tail)))
        except SwitchParsingError, ex:
            print >>sys.stderr, repr(ex)
            print >>sys.stderr
            self.cli_help()
            if exit:
                sys.exit(2)
            else:
                raise
        
        rc = self.main(*tail)
        if exit:
            sys.exit(rc)
        else:
            return rc
    
    def main(self):
        raise NotImplementedError()
    
    @switch(["h", "help"])
    def cli_help(self):
        pass
    
    @switch(["v", "version"])
    def cli_help(self):
        pass


class Application(CliApplication):
    def __init__(self, root):
        CliApplication.__init__(self)
        self.root = root

    def main(self, *tail_args):
        self._tail_args = tail_args
        with Terminal() as term:
            while True:
                evt = term.get_event()
                if evt == ResizedEvent:
                    root_canvas = term.get_root_canvas()
                    self.root.remodel(root_canvas)
                else:
                    self.root.on_event(evt)
                self.root.render()
                root_canvas.commit()


if __name__ == "__main__":
    from widgets import *
    
    r = VLayout(
        HLayout(Label("hello"), Label("world")),
        HLayout(Label("ford"), Label("bord")),
    )
    app = Application(r)
    app.run()




