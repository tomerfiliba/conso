class TerminalEvent(object):
    __slots__ = []


SHIFT = 1
CTRL = 2
ALT = 4

KEY_ESC = "esc"
KEY_ENTER = "enter"
KEY_BACKSPACE = "bksp"
KEY_SPACE = " "
KEY_TAB = "tab"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_UP = "up"
KEY_DOWN = "down"
KEY_INSERT = "insert"
KEY_HOME = "home"
KEY_DELETE = "delete"
KEY_END = "end"
KEY_PAGEUP = "pgup"
KEY_PAGEDOWN = "pgdn"
KEY_F1 = "f1"
KEY_F2 = "f2"
KEY_F3 = "f3"
KEY_F4 = "f4"
KEY_F5 = "f5"
KEY_F6 = "f6"
KEY_F7 = "f7"
KEY_F8 = "f8"
KEY_F9 = "f9"
KEY_F10 = "f10"
KEY_F11 = "f11"
KEY_F12 = "f12"
KEY_F13 = "f13"
KEY_F14 = "f14"
KEY_F15 = "f15"
KEY_F16 = "f16"
KEY_F17 = "f17"
KEY_F18 = "f18"
KEY_F19 = "f19"
KEY_F20 = "f20"

KEYS_BY_NAME = {
    "escape" : KEY_ESC,
    "bksp" : KEY_BACKSPACE,
    "ins" : KEY_INSERT,
    "home" : KEY_HOME,
    "del" : KEY_DELETE,
    "pgup" : KEY_PAGEUP,
    "pgdn" : KEY_PAGEDOWN,
    "page_up" : KEY_PAGEUP,
    "page_down" : KEY_PAGEDOWN,
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

for k, v in globals().items():
    if k.startswith("KEY_"):
        KEYS_BY_NAME[k[4:].lower()] = v

MODIFIER_NAMES = {"ctrl" : CTRL, "control" : CTRL, "meta" : ALT, "alt" : ALT, "shift" : SHIFT}


class KeyEvent(TerminalEvent):
    __slots__ = ["name", "flags"]
    def __init__(self, name, flags = 0):
        self.name = name
        self.flags = flags
    
    @classmethod
    def _canonize_keystring(cls, text):
        if not text:
            return "", 0
        
        attrs = text.split()
        i = text.rfind(" ")
        if i >= 0:
            attrs = text[:i].split()
            name = text[i+1:].strip()
        else:
            attrs = []
            name = text
        
        flags = 0
        for attr in attrs:
            flags |= MODIFIER_NAMES[attr.lower()]
        
        if len(name) > 1:
            name = name.lower()
        if name == "space":
            name = " "
        if (flags, name) in canonization_table:
            flags, name = canonization_table[flags, name]
        if len(name) > 1:
            name = KEYS_BY_NAME[name]
        return name, flags    
    
    @classmethod
    def from_string(cls, text):
        name, flags = cls._canonize_keystring(text)
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
            return (self.name, self.flags) == self._canonize_keystring(other)
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


class ResizedEvent(TerminalEvent):
    __slots__ = []
    def __repr__(self):
        return "<%s>" % (self.__class__.__name__,)
ResizedEvent = ResizedEvent()


def _get_mouse_1(byte1):
    def _get_mouse_2(byte2):
        def _get_mouse_3(byte3):
            return MouseEvent._parse(byte1, byte2, byte3)
        return _get_mouse_3
    return _get_mouse_2

sequences = {
    "\x1b[Z" : KeyEvent(KEY_TAB, SHIFT),
    "\x1b[E" : KeyEvent(u"5"),
    "\x1b[F" : KeyEvent(KEY_END),
    "\x1b[G" : KeyEvent(u"5"),
    "\x1b[H" : KeyEvent(KEY_HOME),
    "\x1bOA" : KeyEvent(KEY_UP),
    "\x1bOB" : KeyEvent(KEY_DOWN),
    "\x1bOC" : KeyEvent(KEY_RIGHT),
    "\x1bOD" : KeyEvent(KEY_LEFT),
    "\x1bOH" : KeyEvent(KEY_HOME),
    "\x1bOF" : KeyEvent(KEY_END),
    "\x1bOo" : KeyEvent(u"/"),
    "\x1bOj" : KeyEvent(u"*"),
    "\x1bOm" : KeyEvent(u"-"),
    "\x1bOk" : KeyEvent(u"+"),
    "\x1bOM" : KeyEvent(KEY_ENTER),
    
    "\x08" : KeyEvent(KEY_BACKSPACE), # h
    "\x09" : KeyEvent(KEY_TAB),       # i
    "\x0d" : KeyEvent(KEY_ENTER),     # m
    "\x1b" : KeyEvent(KEY_ESC),       # [
    "\x7f" : KeyEvent(KEY_BACKSPACE),

    "\x1b\x08" : KeyEvent(KEY_BACKSPACE, ALT), # h
    "\x1b\x09" : KeyEvent(KEY_TAB, ALT),       # i
    "\x1b\x0d" : KeyEvent(KEY_ENTER, ALT),     # m
    "\x1b\x1b" : KeyEvent(KEY_ESC, ALT),       # [
    "\x1b\x7f" : KeyEvent(KEY_BACKSPACE, ALT),
    
    "\x1b[M" : _get_mouse_1,
}

for k, ch in [
        ("\x00", u" "), ("\x01", u"a"), ("\x02", u"b"), ("\x03", u"c"),
        ("\x04", u"d"), ("\x05", u"e"), ("\x06", u"f"), ("\x07", u"g"),
        ("\x0a", u"j"), ("\x0b", u"k"), ("\x0c", u"l"), ("\x0e", u"n"),
        ("\x0f", u"o"), ("\x10", u"p"), ("\x11", u"q"), ("\x12", u"r"),
        ("\x13", u"s"), ("\x14", u"t"), ("\x15", u"u"), ("\x16", u"v"),
        ("\x17", u"w"), ("\x18", u"x"), ("\x19", u"y"), ("\x1a", u"z"),
        ("\x1c", u"|"), ("\x1d", u"]"), ("\x1e", u"6"), ("\x1f", u"?")]:
    sequences[k] = KeyEvent(ch, CTRL)
    sequences["\x1b" + k] = KeyEvent(ch, CTRL | ALT)

MODIFIERS = (("1", SHIFT), ("2", SHIFT), ("3", ALT), ("4", ALT|SHIFT), ("5", CTRL), 
    ("6", CTRL|SHIFT), ("7", CTRL|ALT), ("8", CTRL|ALT|SHIFT))

for code, name in (("A", KEY_UP), ("B", KEY_DOWN), ("C", KEY_RIGHT), ("D", KEY_LEFT)):
    sequences["\x1b[%s" % (code,)] = KeyEvent(name)
    sequences["\x1b[1;%s" % (code,)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        sequences["\x1b[1;%s%s" % (fcode, code)] = KeyEvent(name, flag)

for code, name in (("1", KEY_HOME), ("2", KEY_INSERT), ("3", KEY_DELETE), ("4", KEY_END), 
        ("5", KEY_PAGEUP), ("6", KEY_PAGEDOWN), ("7", KEY_HOME), ("8", KEY_END)):
    sequences["\x1b[%s~" % (code)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        sequences["\x1b[%s;%s~" % (code, fcode)] = KeyEvent(name, flag)

for code, name in (("P", KEY_F1), ("Q", KEY_F2), ("R", KEY_F3), ("S", KEY_F4)):
    sequences["\x1bO%s" % (code)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        sequences["\x1bO%s%s" % (fcode, code)] = KeyEvent(name, flag)
        sequences["\x1bO1;%s%s" % (fcode, code)] = KeyEvent(name, flag)

for code, name in [      ("11", KEY_F1),  ("12", KEY_F2),  ("13", KEY_F3), ("14", KEY_F4), 
        ("15", KEY_F5),  ("17", KEY_F6),  ("18", KEY_F7),  ("19", KEY_F8), ("20", KEY_F9), 
        ("21", KEY_F10), ("23", KEY_F11), ("24", KEY_F12), ("25", KEY_F13), 
        ("26", KEY_F14), ("28", KEY_F15), ("29", KEY_F16), ("31", KEY_F17), 
        ("32", KEY_F18), ("33", KEY_F19), ("34", KEY_F20)]:
    sequences["\x1b[%s~" % (code)] = KeyEvent(name)
    for fcode, flag in MODIFIERS:
        sequences["\x1b[%s;%s~" % (code, fcode)] = KeyEvent(name, flag)


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


terminal_keys_trie = KeysTrie(sequences)


