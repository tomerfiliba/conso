class TerminalEvent(object):
    __slots__ = []

class ResizedEvent(TerminalEvent):
    __slots__ = []
    def __repr__(self):
        return "<%s>" % (self.__class__.__name__,)
ResizedEvent = ResizedEvent()


SHIFT = 1
CTRL = 2
ALT = 4

MODIFIERS = (("1", SHIFT), ("2", SHIFT), ("3", ALT), ("4", ALT|SHIFT), ("5", CTRL), 
    ("6", CTRL|SHIFT), ("7", CTRL|ALT), ("8", CTRL|ALT|SHIFT))

class KeyEvent(TerminalEvent):
    __slots__ = ["name", "flags"]
    def __init__(self, name, flags = 0):
        self.name = name
        self.flags = flags
    @classmethod
    def from_string(cls, text):
        attrs = text.split()
        names = {"ctrl" : CTRL, "control" : CTRL, "meta" : ALT, "alt" : ALT, "shift" : SHIFT}
        flags = 0
        for attr in attrs[:-1]:
            flags |= names.get(attr.lower(), 0)
        return cls(attrs[-1], flags)

    def __repr__(self):
        return "KeyEvent(%r, %r)" % (self.name, self.flags)
    def __str__(self):
        attrs = []
        if self.flags & CTRL:
            attrs.append("ctrl")
        if self.flags & ALT:
            attrs.append("alt")
        if self.flags & SHIFT:
            attrs.append("shift")
        attrs.append(repr(self.name))
        return "<" + " ".join(attrs) + ">"

    def __eq__(self, other):
        if isinstance(other, KeyEvent):
            return self.name == other.name and self.flags == other.flags
        elif isinstance(other, basestring):
            return self == self.from_string(other)
        else:
            return NotImplemented
    def __ne__(self, other):
        return not (self == other)

InvalidKeyEvent = KeyEvent(u"\ufffd")


class MouseEvent(TerminalEvent):
    __slots__ = ["x", "y", "btn", "flags"]
    BTN1 = 1
    BTN2 = 2
    BTN3 = 3
    BTN4 = 4
    BTN5 = 5
    BTN_RELEASE = -1
    _raw_to_button = {0 : BTN1, 1 : BTN2, 2 : BTN3, 3 : BTN_RELEASE,
        64 : BTN4, 65 : BTN5}
    
    def __init__(self, x, y, btn, flags = 0):
        self.x = x
        self.y = y
        self.btn = btn
        self.flags = flags
    
    def __repr__(self):
        if self.flags:
            return "MouseEvent(%r, %r, %r, %r)" % (self.x, self.y, self.btn, self.flags)
        else:
            return "MouseEvent(%r, %r, %r)" % (self.x, self.y, self.btn)
    
    @classmethod
    def _parse(cls, b1, b2, b3):
        b = ord(b1) - 32
        x = ord(b2) - 33
        y = ord(b3) - 33
        btn = cls._raw_to_button[(b & 3) | (((b >> 6) & 1) << 6)]
        flags = (SHIFT if b & 4 else 0) | (ALT if b & 8 else 0) | (CTRL if b & 16 else 0)
        return cls(x, y, btn, flags)

def _get_mouse_1(byte1):
    def _get_mouse_2(byte2):
        def _get_mouse_3(byte3):
            return MouseEvent._parse(byte1, byte2, byte3)
        return _get_mouse_3
    return _get_mouse_2


keys = {
    "\x00" : KeyEvent(" ", CTRL),
    "\x01" : KeyEvent("a", CTRL),
    "\x02" : KeyEvent("b", CTRL),
    "\x03" : KeyEvent("c", CTRL),
    "\x04" : KeyEvent("d", CTRL),
    "\x05" : KeyEvent("e", CTRL),
    "\x06" : KeyEvent("f", CTRL),
    "\x07" : KeyEvent("g", CTRL),
    "\x08" : KeyEvent("backspace"), # h
    "\x09" : KeyEvent("tab"),       # i
    "\x0a" : KeyEvent("j", CTRL),
    "\x0b" : KeyEvent("k", CTRL),
    "\x0c" : KeyEvent("l", CTRL),
    "\x0d" : KeyEvent("enter"),     # m
    "\x0e" : KeyEvent("n", CTRL),
    "\x0f" : KeyEvent("o", CTRL),
    "\x10" : KeyEvent("p", CTRL),
    "\x11" : KeyEvent("q", CTRL),
    "\x12" : KeyEvent("r", CTRL),
    "\x13" : KeyEvent("s", CTRL),
    "\x14" : KeyEvent("t", CTRL),
    "\x15" : KeyEvent("u", CTRL),
    "\x16" : KeyEvent("v", CTRL),
    "\x17" : KeyEvent("w", CTRL),
    "\x18" : KeyEvent("x", CTRL),
    "\x19" : KeyEvent("y", CTRL),
    "\x1a" : KeyEvent("z", CTRL),
    "\x1b" : KeyEvent("esc"),       # [
    "\x1c" : KeyEvent("\\", CTRL),  # \ |
    "\x1d" : KeyEvent("]", CTRL),
    "\x1e" : KeyEvent("6", CTRL),
    "\x1f" : KeyEvent("?", CTRL),
    "\x7f" : KeyEvent("backspace"),
    
    "\x1b[Z" : KeyEvent("tab", SHIFT),
    "\x1b[E" : KeyEvent("5"),
    "\x1b[F" : KeyEvent("end"),
    "\x1b[G" : KeyEvent("5"),
    "\x1b[H" : KeyEvent("home"),
    "\x1bOA" : KeyEvent("up"),
    "\x1bOB" : KeyEvent("down"),
    "\x1bOC" : KeyEvent("right"),
    "\x1bOD" : KeyEvent("left"),
    "\x1bOH" : KeyEvent("home"),
    "\x1bOF" : KeyEvent("end"),
    "\x1bOo" : KeyEvent("/"),
    "\x1bOj" : KeyEvent("*"),
    "\x1bOm" : KeyEvent("-"),
    "\x1bOk" : KeyEvent("+"),
    "\x1bOM" : KeyEvent("enter"),
    
    "\x1b[M" : _get_mouse_1,
}

for code, name in (("A", "up"), ("B", "down"), ("C", "right"), ("D", "left")):
    keys["\x1b[%s" % (code,)] = KeyEvent(name)
    keys["\x1b[1;%s" % (code,)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        keys["\x1b[1;%s%s" % (fcode, code)] = KeyEvent(name, flag)

for code, name in (("1", "home"), ("2", "insert"), ("3", "delete"), ("4", "end"), 
        ("5", "pageup"), ("6", "pagedown"), ("7", "home"), ("8", "end")):
    keys["\x1b[%s~" % (code)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        keys["\x1b[%s;%s~" % (code, fcode)] = KeyEvent(name, flag)

for code, name in (("P", "f1"), ("Q", "f2"), ("R", "f3"), ("S", "f4")):
    keys["\x1bO%s" % (code)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        keys["\x1bO%s%s" % (fcode, code)] = KeyEvent(name, flag)
        keys["\x1bO1;%s%s" % (fcode, code)] = KeyEvent(name, flag)

for code, name in (("11", "f1"), ("12", "f2"), ("13", "f3"), ("14", "f4"), ("14", "f4"), 
        ("15", "f5"), ("17", "f6"), ("18", "f7"), ("19", "f8"), ("20", "f9"), ("21", "f10"), 
        ("23", "f11"), ("24", "f12"), (25, "f13"), (26, "f14"), (28, "f15"), (29, "f16"), 
        (31, "f17"), (32, "f18"), (33, "f19"), (34, "f20")):
    keys["\x1b[%s~" % (code)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        keys["\x1b[%s;%s~" % (code, fcode)] = KeyEvent(name, flag)


class KeysTrie(object):
    def __init__(self, keys):
        self.root = {}
        for seq, info in keys.iteritems():
            self._build_trie(self.root, list(seq), info)
        self._minimize_trie(self.root)
        self.reset()
    
    @classmethod
    def _build_trie(cls, mapping, seq, value):
        if not seq:
            if None in mapping:
                raise ValueError("seq already defined")
            mapping[None] = value
        else:
            item = seq.pop(0)
            if item not in mapping:
                mapping[item] = {}
            cls._build_trie(mapping[item], seq, value)
    
    @classmethod
    def _minimize_trie(cls, mapping):
        for k, v in mapping.iteritems():
            if isinstance(v, dict):
                if len(v) == 1 and None in v:
                    mapping[k] = v[None]
                else:
                    cls._minimize_trie(v)
    
    def reset(self):
        self.state = self.root
        self.stack = []
    
    def _decode(self, char):
        self.stack.append(char)
        if callable(self.state):
            next = self.state(char)
            if callable(next):
                self.state = next
                return None
            else:
                self.reset()
                return next
        elif char not in self.state:
            if len(self.stack) == 1:
                self.reset()
                return KeyEvent(char)
            elif len(self.stack) == 2 and self.stack[0] == "\x1b":
                self.reset()
                return KeyEvent(char, ALT)
            else:
                self.reset()
                return InvalidKeyEvent
        else:
            next = self.state[char]
            if isinstance(next, dict) or callable(next):
                self.state = next
                return None
            else:
                self.reset()
                return next
    
    def decode(self, data = None):
        for char in data:
            output = self._decode(char)
            if output:
                yield output
    
    def pull(self):
        return self._decode(None)


terminal_keys_trie = KeysTrie(keys)



