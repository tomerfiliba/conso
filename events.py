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
        name, flags = canonize_keystring(text)
        return cls(name, flags)

    def as_char(self):
        if self.flags == 0 and len(self.name) == 1:
            return self.name
        return None

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
            return (self.name, self.flags) == canonize_keystring(other)
        else:
            return NotImplemented
    def __ne__(self, other):
        return not (self == other)
    def __hash__(self):
        return hash(self.name)

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
    "\x1b[Z" : KeyEvent(u"tab", SHIFT),
    "\x1b[E" : KeyEvent(u"5"),
    "\x1b[F" : KeyEvent(u"end"),
    "\x1b[G" : KeyEvent(u"5"),
    "\x1b[H" : KeyEvent(u"home"),
    "\x1bOA" : KeyEvent(u"up"),
    "\x1bOB" : KeyEvent(u"down"),
    "\x1bOC" : KeyEvent(u"right"),
    "\x1bOD" : KeyEvent(u"left"),
    "\x1bOH" : KeyEvent(u"home"),
    "\x1bOF" : KeyEvent(u"end"),
    "\x1bOo" : KeyEvent(u"/"),
    "\x1bOj" : KeyEvent(u"*"),
    "\x1bOm" : KeyEvent(u"-"),
    "\x1bOk" : KeyEvent(u"+"),
    "\x1bOM" : KeyEvent(u"enter"),
    
    "\x08" : KeyEvent(u"backspace"), # h
    "\x09" : KeyEvent(u"tab"),       # i
    "\x0d" : KeyEvent(u"enter"),     # m
    "\x1b" : KeyEvent(u"esc"),       # [
    "\x7f" : KeyEvent(u"backspace"),

    "\x1b\x08" : KeyEvent(u"backspace", ALT), # h
    "\x1b\x09" : KeyEvent(u"tab", ALT),       # i
    "\x1b\x0d" : KeyEvent(u"enter", ALT),     # m
    "\x1b\x1b" : KeyEvent(u"esc", ALT),       # [
    "\x1b\x7f" : KeyEvent(u"backspace", ALT),
    
    "\x1b[M" : _get_mouse_1,
}

canonization_table = {
    (CTRL, "i")     : (0, u"tab"),
    (CTRL, "enter") : (CTRL, u"j"),
    (CTRL, "7")     : (CTRL, u"?"),
    (CTRL, "[")     : (0, u"esc"),
    (CTRL, "h")     : (0, u"backspace"),
    (CTRL, "8")     : (0, u"backspace"),
    (CTRL, "`")     : (CTRL, u" "),
    (CTRL, "~")     : (CTRL, u" "),
    (CTRL, "2")     : (CTRL, u" "),
    (CTRL, "-")     : (CTRL, u" "),
    (CTRL, "m")     : (0, u"enter"),
    (CTRL, "4")     : (CTRL, u"|"),
    (CTRL, "5")     : (CTRL, u"]"),
    (CTRL, "7")     : (CTRL, u"?"),
}

ATTR_NAMES = {"ctrl" : CTRL, "control" : CTRL, "meta" : ALT, "alt" : ALT, "shift" : SHIFT}

def canonize_keystring(text):
    if not text:
        return "", 0
    
    attrs = text.split()
    i = text.rfind(" ")
    attrs = text[:i].split()
    name = text[i+1:].strip()
    
    flags = 0
    for attr in attrs:
        flags |= ATTR_NAMES[attr.lower()]
    
    if len(name) > 1:
        name = name.lower()
    if name == "space":
        name = " "
    if (flags, name) in canonization_table:
        flags, name = canonization_table[flags, name]
    return name, flags


for k, ch in [("\x00", u" "), ("\x01", u"a"), ("\x02", u"b"), ("\x03", u"c"),
        ("\x04", u"d"), ("\x05", u"e"), ("\x06", u"f"), ("\x07", u"g"),
        ("\x0a", u"j"), ("\x0b", u"k"), ("\x0c", u"l"), ("\x0e", u"n"),
        ("\x0f", u"o"), ("\x10", u"p"), ("\x11", u"q"), ("\x12", u"r"),
        ("\x13", u"s"), ("\x14", u"t"), ("\x15", u"u"), ("\x16", u"v"),
        ("\x17", u"w"), ("\x18", u"x"), ("\x19", u"y"), ("\x1a", u"z"),
        ("\x1c", u"|"), ("\x1d", u"]"), ("\x1e", u"6"), ("\x1f", u"?")]:
    keys[k] = KeyEvent(ch, CTRL)
    keys["\x1b" + k] = KeyEvent(ch, CTRL | ALT)

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
                raise ValueError("sequence already defined")
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



