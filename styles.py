class StyleElement(object):
    __slots__ = ["value", "fallback"]
    def __init__(self, value = None, fallback = None):
        self.value = value
        self.fallback = fallback
    def copy(self):
        return Element(self.value, self.fallback)


class Style(object):
    __slots__ = ["_elements", "_values"]
    
    def __init__(self, **elements):
        for k, v in elements.iteritems():
            if v.fallback and v.fallback not in elements:
                raise ValueError("nonexisting fallback key for %r: %r" % (k, v.fallback))
        object.__setattr__(self, "_elements", elements)
        
    
    def __str__(self):
        elems = "\n    ".join(sorted("%s: %r" % (key, self[key]) for key in self._elements))
        return "Style(\n    %s\n)" % (elems,)
    
    @classmethod
    def from_style(cls, parent, **elements):
        d = dict((name, elem.copy())
            for name, elem in parent._elements.iteritems())
        d.update(elements)
        return cls(**d)
    
    def __getitem__(self, key):
        elem = self._elements[key]
        if elem.value is not None:
            return elem.value
        if elem.fallback is not None:
            return self[elem.fallback]
        return elem.value
    def __setitem__(self, key, value):
        elem = self._elements[key]
        elem.value = value
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttrbuteError("%r: no such element" % (name,))
    def __setattr__(self, name, value):
        try:
            self[name] = value
        except KeyError:
            raise AttrbuteError("%r: no such element" % (name,))


default_style = Style(
    text_color = StyleElement(),
    bg_color = StyleElement(),
    text_color_focused = StyleElement("cyan"),
    border_color = StyleElement(),
    border_color_focused = StyleElement("cyan"),
    
    label_text_color = StyleElement(fallback = "text_color"),
    label_bg_color = StyleElement(fallback = "bg_color"),
    
    labelbox_text_color = StyleElement(fallback = "label_text_color"),
    labelbox_bg_color = StyleElement(fallback = "label_bg_color"),
    
    button_text_color = StyleElement(fallback = "text_color"),
    button_text_color_focused = StyleElement(fallback = "text_color_focused"),
    button_bg_color = StyleElement(fallback = "bg_color"),
    
    textentry_text_color = StyleElement(fallback = "text_color"),
    textentry_text_color_focused = StyleElement(fallback = "text_color_focused"),
    textentry_bg_color = StyleElement(fallback = "bg_color"),
    
    frame_title_color = StyleElement(fallback = "text_color"),
    frame_title_color_focused = StyleElement(fallback = "text_color_focused"),
    frame_border_color = StyleElement(fallback = "border_color"),
    frame_border_color_focused = StyleElement(fallback = "border_color_focused"),
)










