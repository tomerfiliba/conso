SHIFT = 1
CTRL = 2
ALT = 4

MODIFIERS = (("1", SHIFT), ("2", SHIFT), ("3", ALT), ("4", ALT|SHIFT), ("5", CTRL), 
    ("6", CTRL|SHIFT), ("7", CTRL|ALT), ("8", CTRL|ALT|SHIFT))

class KeyInfo(object):
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
        return "KeyInfo(%r, %r)" % (self.name, self.flags)
    def __str__(self):
        attrs = []
        if self.flags & CTRL:
            attrs.append("ctrl")
        if self.flags & ALT:
            attrs.append("alt")
        if self.flags & SHIFT:
            attrs.append("shift")
        attrs.append(self.name)
        return "<" + " ".join(attrs) + ">"

    def __eq__(self, other):
        if isinstance(other, KeyInfo):
            return self.name == other.name and self.flags == other.flags
        elif isinstance(other, basestring):
            return self == self.from_string(other)
        else:
            return NotImplemented
    def __ne__(self, other):
        return not (self == other)

keys = {
    "\x00" : KeyInfo(" ", CTRL),
    "\x01" : KeyInfo("a", CTRL),
    "\x02" : KeyInfo("b", CTRL),
    "\x03" : KeyInfo("c", CTRL),
    "\x04" : KeyInfo("d", CTRL),
    "\x05" : KeyInfo("e", CTRL),
    "\x06" : KeyInfo("f", CTRL),
    "\x07" : KeyInfo("g", CTRL),
    "\x08" : KeyInfo("backspace"), # h
    "\x09" : KeyInfo("tab"),       # i
    "\x0a" : KeyInfo("j", CTRL),
    "\x0b" : KeyInfo("k", CTRL),
    "\x0c" : KeyInfo("l", CTRL),
    "\x0d" : KeyInfo("enter"),     # m
    "\x0e" : KeyInfo("n", CTRL),
    "\x0f" : KeyInfo("o", CTRL),
    "\x10" : KeyInfo("p", CTRL),
    "\x11" : KeyInfo("q", CTRL),
    "\x12" : KeyInfo("r", CTRL),
    "\x13" : KeyInfo("s", CTRL),
    "\x14" : KeyInfo("t", CTRL),
    "\x15" : KeyInfo("u", CTRL),
    "\x16" : KeyInfo("v", CTRL),
    "\x17" : KeyInfo("w", CTRL),
    "\x18" : KeyInfo("x", CTRL),
    "\x19" : KeyInfo("y", CTRL),
    "\x1a" : KeyInfo("z", CTRL),
    "\x1b" : KeyInfo("esc"),       # [
    "\x1c" : KeyInfo("\\", CTRL),  # \ |
    "\x1d" : KeyInfo("]", CTRL),
    "\x1e" : KeyInfo("6", CTRL),
    "\x1f" : KeyInfo("?", CTRL),
    "\x7f" : KeyInfo("backspace"),
    
    "\x1b[Z" : KeyInfo("tab", SHIFT),
    "\x1b[E" : KeyInfo("5"),
    "\x1b[F" : KeyInfo("end"),
    "\x1b[G" : KeyInfo("5"),
    "\x1b[H" : KeyInfo("home"),
    "\x1bOA" : KeyInfo("up"),
    "\x1bOB" : KeyInfo("down"),
    "\x1bOC" : KeyInfo("right"),
    "\x1bOD" : KeyInfo("left"),
    "\x1bOH" : KeyInfo("home"),
    "\x1bOF" : KeyInfo("end"),
    "\x1bOo" : KeyInfo("/"),
    "\x1bOj" : KeyInfo("*"),
    "\x1bOm" : KeyInfo("-"),
    "\x1bOk" : KeyInfo("+"),
    "\x1bOM" : KeyInfo("enter"),
}

for code, name in (("A", "up"), ("B", "down"), ("C", "right"), ("D", "left")):
    keys["\x1b[%s" % (code,)] = KeyInfo(name)
    keys["\x1b[1;%s" % (code,)] = KeyInfo(name)
    for fcode, flag in MODIFIERS:
        keys["\x1b[1;%s%s" % (fcode, code)] = KeyInfo(name, flag)

for code, name in (("1", "home"), ("2", "insert"), ("3", "delete"), ("4", "end"), 
        ("5", "pageup"), ("6", "pagedown"), ("7", "home"), ("8", "end")):
    keys["\x1b[%s~" % (code)] = KeyInfo(name)
    for fcode, flag in MODIFIERS:
        keys["\x1b[%s;%s~" % (code, fcode)] = KeyInfo(name, flag)

for code, name in (("P", "f1"), ("Q", "f2"), ("R", "f3"), ("S", "f4")):
    keys["\x1bO%s" % (code)] = KeyInfo(name)
    for fcode, flag in MODIFIERS:
        keys["\x1bO%s%s" % (fcode, code)] = KeyInfo(name, flag)
        keys["\x1bO1;%s%s" % (fcode, code)] = KeyInfo(name, flag)

for code, name in (("11", "f1"), ("12", "f2"), ("13", "f3"), ("14", "f4"), ("14", "f4"), 
        ("15", "f5"), ("17", "f6"), ("18", "f7"), ("19", "f8"), ("20", "f9"), ("21", "f10"), 
        ("23", "f11"), ("24", "f12"), (25, "f13"), (26, "f14"), (28, "f15"), (29, "f16"), 
        (31, "f17"), (32, "f18"), (33, "f19"), (34, "f20")):
    keys["\x1b[%s~" % (code)] = KeyInfo(name)
    for fcode, flag in MODIFIERS:
        keys["\x1b[%s;%s~" % (code, fcode)] = KeyInfo(name, flag)

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

#    def _print(self, mapping = None, nesting = 0):
#        if mapping is None:
#            mapping = self.root
#        for k, v in mapping.iteritems():
#            if isinstance(v, dict):
#                print nesting * "  " + `k` + ":"
#                self._print(v, nesting + 1)
#            else:
#                print nesting * "  " + `k` + ":", `v`
    
    def reset(self):
        self.state = self.root
        self.stack = []
    
    def _decode(self, char):
        self.stack.append(char)
        if char not in self.state:
            if len(self.stack) == 1:
                self.reset()
                return KeyInfo(char)
            elif len(self.stack) == 2 and self.stack[0] == "\x1b":
                self.reset()
                return KeyInfo(char, ALT)
            else:
                self.reset()
                return KeyInfo(u"\ufffd")
        else:
            next = self.state[char]
            if isinstance(next, dict):
                self.state = next
                return None
            else:
                self.reset()
                return next
    
    def decode(self, data = None):
        if data is None:
            self._decode(None)
        for char in data:
            output = self._decode(char)
            if output:
                yield output

TerminalKeys = KeysTrie(keys)
#for k in trie.decode("\x1b["):
#    print k
















