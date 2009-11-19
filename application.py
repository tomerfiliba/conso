import sys
import inspect
from textwrap import wrap
from .terminal import Terminal
from .events import ResizedEvent


class SwitchParsingError(Exception):
    def __str__(self):
        return self.MSG % self.args
class TooFewTailArgsError(SwitchParsingError):
    MSG = "Application takes at least %r positional arguments, %r given"
class TooManyTailArgsError(SwitchParsingError):
    MSG = "Application takes at most %r positional arguments, %r given"
class DanglingArgsError(SwitchParsingError):
    MSG = "Dangling arguments appear before %r: %r"
class ParameterTypeError(SwitchParsingError):
    MSG = "%r expects a parameter of %r, got %r"
class MissingParameterError(SwitchParsingError):
    MSG = "%r requires a parameter"
class InvalidSwitchError(SwitchParsingError):
    MSG = "Invalid switch given: %r"
class MandatorySwitchNotGiven(SwitchParsingError):
    MSG = "Mandatory switch not given: %r"
class SwitchGivenMoreThanOnce(SwitchParsingError):
    MSG = "Switch %r (or an alias) given more than once"

# XXX: excludes and requires !

def switch(names, type = None, doc = None, multiple = False, mandatory = False, 
        overriding = False, excludes = (), requires = ()):
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
            doc2 = func.__name__
        if type:
            a, va, kw, dfl = inspect.getargspec(func)
            if va:
                paramname = va
            else:
                if len(a) < 2:
                    raise TypeError("switches taking a parameter must accept "
                        "at least one positional argument")
                paramname = a[1]
        else:
            paramname = None
        func._switch_info = dict(names = names, paramtype = type, paramname = paramname, 
            doc = doc2, multiple = multiple, mandatory = mandatory, invoked = False,
            excludes = excludes, requires = requires)
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
            obj = getattr(self.__class__, name, None)
            if not callable(obj) or not hasattr(obj, "_switch_info"):
                continue
            swinfo = obj._switch_info
            for key in swinfo["names"]:
                if key in self._switches and not swinfo["overriding"]:
                    raise ValueError("multiple switches register the same "
                        "name: %r" % (name,))
                self._switches[key] = (obj, swinfo)
    
    def _parse_cli_args(self, argv):
        tail = []
        while argv:
            arg = argv.pop(0)
            param = None
            if arg == self.END_OF_SWITCHES:
                if tail:
                    raise DanglingArgsError(arg, tail)
                return argv
            elif arg.startswith(self.LONG_SWITCH_PREFIX):
                if tail:
                    raise DanglingArgsError(arg, tail)
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
                    raise DanglingArgsError(arg, tail)
                arg = arg[len(self.SHORT_SWITCH_PREFIX):]
                if len(arg) > 1:
                    arg = arg[0]
                    rest = arg[1:]
                    argv.insert(0, self.SHORT_SWITCH_PREFIX + rest)
                self._invoke_switch(arg, argv)
            else:
                tail.append(arg)
        
        for swobj, swinfo in self._switches.itervalues():
            if swinfo["mandatory"] and not swinfo["invoked"]:
                raise MandatorySwitchNotGiven(swinfo["names"][0])
        
        return tail
    
    def _invoke_switch(self, sw, argv):
        if sw not in self._switches:
            raise InvalidSwitchError(sw)
        swobj, swinfo = self._switches[sw]
        if swinfo["invoked"] and not swinfo["multiple"]:
            raise SwitchGivenMoreThanOnce(sw)
        swinfo["invoked"] = True
        if swinfo["paramtype"]:
            if not argv:
                raise MissingParameterError(sw)
            param = argv.pop(0)
            try:
                param2 = swinfo["paramtype"](param)
            except (TypeError, ValueError), ex:
                raise ParameterTypeError(sw, swinfo["paramtype"], param)
            swobj(self, param2)
        else:
            swobj(self)

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
                    raise TooManyTailArgsError(atmost, len(tail))
                if len(tail) < atleast:
                    raise TooFewTailArgsError(atleast, len(tail))
        except SwitchParsingError, ex:
            print >>sys.stderr, "Error: %s\n" % (ex,)
            self._generate_cli_help(sys.stderr, show_doc = False)
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
    
    def _generate_cli_version(self, file = sys.stdout):
        app_name = self.APP_NAME if self.APP_NAME else self.__class__.__name__
        app_ver = self.APP_VERSION if self.APP_VERSION else "<not set>"
        print >>file, "%s [version %s]" % (app_name, app_ver)

    def _generate_cli_help(self, file = sys.stdout, show_doc = True, width = 79):
        if show_doc:
            app_doc = self.APP_DOC if self.APP_DOC else inspect.getdoc(self)
            if app_doc:
                print >>file, "  " + app_doc + "\n"
        
        info = []
        visited = set()
        for swobj, swinfo in self._switches.values():
            if swobj in visited:
                continue
            visited.add(swobj)
            names = []
            paramname = swinfo["paramname"]
            for n in swinfo["names"]:
                if len(n) == 1:
                    p = " " + paramname if paramname else ""
                    names.append(self.SHORT_SWITCH_PREFIX + n + p)
                else:
                    p = "=" + paramname if paramname else ""
                    names.append(self.LONG_SWITCH_PREFIX + n + p)
            names.sort(key = len)
            doc = " ".join(swinfo["doc"].strip().splitlines())
            if doc[-1] not in ".;!?,":
                doc += "."
            if paramname:
                doc += " '%s' is %s." % (paramname, swinfo["paramtype"])
            info.append((", ".join(names), doc))
        
        main_args, va, kw, dfl = inspect.getargspec(self.main)
        main_args.pop(0) # 'self'
        if va:
            main_args.append("%s..." % (va,))
        
        if info:
            print >>file, "Usage: %s OPTIONS %s" % (self._exe_name, " ".join(main_args,))
        else:
            print >>file, "Usage: %s %s" % (self._exe_name, " ".join(main_args,))
            return
        
        info.sort(key = lambda item: item[0].strip(self.LONG_SWITCH_PREFIX).strip(self.SHORT_SWITCH_PREFIX))
        longest = min(max(len(swname) for swname, doc in info), 30)
        pattern = "  %%-%ds  " % (longest,)
        start_wrap = 2 + longest + 2
        for swnames, doc in info:
            prefix = pattern % (swnames)
            lines = wrap(doc, width - len(prefix))
            first = lines[0]
            rest = wrap(" ".join(lines[1:]), width - start_wrap)
            print >>file, prefix + first
            if rest:
                print >>file, "\n".join([" " * start_wrap + line for line in rest])
    
    @switch(["h", "help"])
    def cli_help(self):
        """show this help message and quit"""
        self._generate_cli_version()
        self._generate_cli_help()
        sys.exit(0)
    
    @switch(["v", "version"])
    def cli_version(self):
        """print the application's version and quit"""
        self._generate_cli_version()
        sys.exit(0)

    
class Application(CliApplication):
    def __init__(self, root, style = {}):
        CliApplication.__init__(self)
        self.root = root
        self.style = style

    def main(self):
        self._mainloop()
        return 0

    def _mainloop(self):
        with Terminal() as term:
            while True:
                evt = term.get_event()
                if evt == ResizedEvent:
                    root_canvas = term.get_root_canvas()
                    self.root.remodel(root_canvas)
                    term.clear_screen()
                elif evt == "ctrl q":
                    break
                else:
                    self.root.on_event(evt)
                self.root.render(self.style, focused = True)
                root_canvas.commit()
            term.clear_screen()





