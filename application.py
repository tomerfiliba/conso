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
        if not isinstance(n, basestring):
            raise ValueError("name must be a string: %r" % (n,))
    def deco(func):
        doc2 = doc
        if not doc:
            doc2 = inspect.getdoc(func)
        if not doc2:
            doc2 = repr(func)
        if type:
            a, va, kw, dfl = inspect.getargspec(func)
            if va:
                paramname = va
            else:
                if len(a) < 2:
                    raise TypeError("switches taking a parameter must accept at least one positional argument")
                paramname = a[1]
        else:
            paramname = None
        func._switch_info = dict(names = names, paramtype = type, paramname = paramname, 
            doc = doc2, multiple = multiple, required = required, invoked = False)
        return func
    return deco


class CliApplication(object):
    SHORT_SWITCH_PREFIX = "-"
    LONG_SWITCH_PREFIX = "--"
    END_OF_SWITCHES = "--"
    
    APP_NAME = None
    APP_VERSION = None
    APP_DOC = None
    
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
                arg = arg[len(self.LONG_SWITCH_PREFIX):]
                if "=" in arg:
                    sw, arg = arg.split("=", 1)
                    argv.insert(0, arg)
                    arg = sw
                if argv and argv[0] == "=":
                    argv.pop(0)
                self._invoke_switch(arg, argv)
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
        if swinfo["paramtype"]:
            if not argv:
                raise MissingParameterError("expected a parameter to follow %r" % (sw,))
            param = argv.pop(0)
            try:
                param = swinfo["paramtype"](param)
            except (TypeError, ValueError), ex:
                raise ParameterTypeError("invalid parameter type for %r; expected %r" % (sw, swinfo["paramtype"]))
            swobj(param)
        else:
            swobj()

    def _parse_short_switch(self, sw, argv):
        if len(arg) > 1:
            arg = arg[0]
            rest = arg[1:]
            swobj, swinfo = self._switches[arg]
            if swinfo["paramtype"]:
                param = swinfo["paramtype"](rest)
                swobj(rest)
            else:
                argv.insert(0, self.SHORT_SWITCH_PREFIX + rest)
                swobj()
        else:
            swobj, swinfo = self._switches[arg]
            if swinfo["paramtype"]:
                param = swinfo["paramtype"](rest)
                swobj(param)
            else:
                swobj()
    
    def run(self, argv = None, exit = True):
        if not argv:
            argv = sys.argv
        self._exe_name = argv[0]
        args = argv[1:]
        
        try:
            tail = self._parse_cli_args(args)
            a, va, kw, dfl = inspect.getargspec(self.main)
            if not va:
                atmost = len(a) - 1
                atleast = atmost - (len(dfl) if dfl else 0)
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
    
    def _generate_cli_version(self):
        app_name = self.APP_NAME if self.APP_NAME else self.__class__.__name__
        app_ver = self.APP_VERSION if self.APP_VERSION else "<not set>"
        print "%s [version %s]" % (app_name, app_ver)

    def _generate_cli_help(self, width = 78):
        self._generate_cli_version()
        app_doc = self.APP_DOC if self.APP_DOC else inspect.getdoc(self)
        if app_doc:
            print
            print app_doc
        
        info = []
        for _, swinfo in self._switches.values():
            names = []
            paramname = swinfo["paramname"]
            for n in swinfo["names"]:
                if len(n) == 1:
                    p = " " + paramname if paramname else ""
                    names.append(self.SHORT_SWITCH_PREFIX + n + p)
                else:
                    p = "==" + paramname if paramname else ""
                    names.append(self.LONG_SWITCH_PREFIX + n + p)
            names.sort(key = len)
            doc = swinfo["doc"]
            info.append((", ".join(names), doc))
        
        if not info:
            return
        
        print
        print "%s OPTIONS... <args>" % (self._exe_name,)
        info.sort(key = lambda item: item[0])
        longest = min(max(len(swname) for swname, doc in info), 30)
        pattern = "  %%-%ds  %%s" % (longest,)
        start_wrap = 2 + longest + 2
        for swnames, doc in info:
            line = pattern % (swnames, doc)
            first = line[:width]
            rest = line[width:]
            text = [first]
            if rest:
                available = width - start_wrap
                for i in range(0, len(rest), available):
                    text.append(start_wrap * " " + rest[i:i+available])
            print "\n".join(text)
    
    @switch(["h", "help"])
    def cli_help(self):
        """show this help message and quit"""
        self._generate_cli_help()
        sys.exit(0)
    
    @switch(["v", "version"])
    def cli_version(self):
        """print the application's version and quit and tell and very long long long story about the little dog who ran to the forest"""
        self._generate_cli_help()
        sys.exit(0)


class Application(CliApplication):
    def __init__(self, root):
        CliApplication.__init__(self)
        self.root = root

    def main(self):
        self._mainloop()
    
    def _mainloop(self):
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
        HLayout(Label("ford"), Label("bord"), Label("moshe")),
    )
    app = Application(r)
    app.run()




