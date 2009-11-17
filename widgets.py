from events import KeyEvent, MouseEvent


class Widget(object):
    priority = 500
    
    def on_event(self, evt):
        if isinstance(evt, KeyEvent):
            return self._on_key(evt)
        elif isinstance(evt, MouseEvent):
            return self._on_mouse(evt)
        else:
            return False
    def _on_key(self, evt):
        return False
    def _on_mouse(self, evt):
        return False
    
    def can_get_focus(self):
        return False
    
    def get_min_size(self, pwidth, pheight):
        raise NotImplementedError()
    def get_desired_size(self, pwidth, pheight):
        raise NotImplementedError()
    def remodel(self, canvas):
        raise NotImplementedError()
    def render(self, focused = False, highlight = False):
        raise NotImplementedError()


class Label(Widget):
    def __init__(self, text, fg = None, bg = None):
        self.text = text
        self.fg = fg
        self.bg = bg
    def get_min_size(self, pwidth, pheight):
        return (max(3, len(self.text)), 1)
    def get_desired_size(self, pwidth, pheight):
        return (len(self.text), 1)
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, focused = False, highlight = False):
        padded = self.text + " " * (self.canvas.width - len(self.text))
        self.canvas.write(0, 0, padded, fg = self.fg, bg = self.bg, inversed = highlight)

class TextEntry(Widget):
    def __init__(self, text = "", max_length = None):
        self.text = text
        self.max_length = max_length
        self.cursor_offset = 0
        self.start_offset = None
        self.end_offset = None
    def remodel(self, canvas):
        self.canvas = canvas
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, 1)
    def get_min_size(self, pwidth, pheight):
        return (3, 1)
    def render(self, focused = True, highlight = False):
        w = self.canvas.width
        
        if self.cursor_offset > self.end_offset or self.cursor_offset < self.start_offset:
            self.end_offset = min(len(self.text), self.cursor_offset + w)
            self.start_offset = max(0, self.end_offset - w)
        visible = self.text[self.start_offset:self.end_offset]
        
        if focused:
            rel_cursor = max(0, self.cursor_offset - self.start_offset)
            if rel_cursor >= len(visible):
                if len(self.text) >= w:
                    before = visible[1:]
                else:
                    before = visible
                under = self.canvas.DOT
                after = ""
            else:
                before = visible[:rel_cursor]
                under = visible[rel_cursor]
                after = visible[rel_cursor+1:]
            after += self.canvas.DOT * (w - len(visible) - 1)
            self.canvas.write(0, 0, before, inversed = highlight)
            self.canvas.write(len(before), 0, under, underlined = True, inversed = highlight)
            self.canvas.write(len(before) + 1, 0, after, inversed = highlight)
        else:
            self.canvas.write(0, 0, visible, inversed = highlight)
    
    def _on_key(self, evt):
        if evt == "left" and self.cursor_offset >= 1:
            self.cursor_offset -= 1
            return True
        elif evt == "right" and self.cursor_offset <= len(self.text) - 1:
            self.cursor_offset += 1
            return True
        elif evt == "backspace" and self.cursor_offset >= 1:
            before = self.text[:self.cursor_offset-1]
            after = self.text[self.cursor_offset:]
            self.cursor_offset -= 1
            self.text = before + after
            return True
        elif evt == "delete" and len(self.text) > self.cursor_offset:
            before = self.text[:self.cursor_offset]
            after = self.text[self.cursor_offset+1:]
            self.text = before + after
            return True
        elif evt == "home":
            self.cursor_offset = 0
        elif evt == "end":
            self.cursor_offset = len(self.text)
        elif not self.max_length or len(self.text) < self.max_length:
            ch = evt.as_char()
            if ch:
                before = self.text[:self.cursor_offset]
                after = self.text[self.cursor_offset:]
                self.text = before + ch + after
                self.cursor_offset += 1
                return True
        return False


class ListModel(object):
    def hasitem(self, index):
        raise NotImplementedError()
    def getitem(self, index):
        raise NotImplementedError()

class SimpleListModel(object):
    def __init__(self, list):
        self.list = list
    def hasitem(self, index):
        return index >= 0 and index < len(self.list)
    def getitem(self, index):
        return Label(self.list[index])

class ListBox(Widget):
    priority = 501
    
    def __init__(self, model):
        self.model = model
        self.start_index = 0
        self.last_index = None
        self.selected_index = 0
    def get_min_size(self, pwidth, pheight):
        return (5, 2)
    def get_desired_size(self, pwidth, pheight):
        return (pwidth, pheight)
    def remodel(self, canvas):
        self.canvas = canvas
    def render(self, focused = False, highlight = False):
        offy = 0
        if self.selected_index < self.start_index or self.selected_index > self.last_index:
            self.last_index = None
            self.start_index = max(0, self.selected_index - 5)
        i = self.start_index
        while self.model.hasitem(i) and offy < self.canvas.height:
            self.last_index  = i
            item = self.model.getitem(i)
            dw, dh = item.get_desired_size(self.canvas.width, self.canvas.height)
            canvas2 = self.canvas.subcanvas(0, offy, dw, dh)
            item.remodel(canvas2)
            item.render(highlight = focused and (i == self.selected_index))
            i += 1
            offy += canvas2.height
    
    def _on_key(self, evt):
        if evt == "down" and self.model.hasitem(self.selected_index + 1):
            self.selected_index += 1
            return True
        elif evt == "up" and self.selected_index >= 1:
            self.selected_index -= 1
            return True
        elif evt == "pagedown":
            if not self.model.hasitem(self.selected_index + 1):
                return False
            self.selected_index += 1
            for i in range(2, self.canvas.height):
                if not self.model.hasitem(self.selected_index + 1):
                    break
                self.selected_index += 1
            return True
        elif evt == "pageup" and self.selected_index >= 1:
            self.selected_index = max(0, self.selected_index - self.canvas.height)
            return True
        return False

class Layout(Widget):
    HORIZONTAL = 0
    VERTICAL = 1
    
    def __init__(self, axis, widgets):
        self.axis = axis
        self.widgets = widgets
        self.selected_index = None
    
    def get_min_size(self, pwidth, pheight):
        sizes = [w.get_min_size(pwidth, pheight) for w in self.widgets]
        w = sum(s[self.axis] for s in sizes)
        h = max(s[1 - self.axis] for s in sizes)
        return w, h
    
    def _calc_visible_widgets(self, total_size):
        widgets = sorted(self.widgets, key = lambda w: w.priority)
        while True:
            output = []
            total_priorities = float(sum(w.priority for w in widgets))
            accumulated_size = 0
            for i, wgt in enumerate(widgets):
                alloted = int(round(total_size * wgt.priority / total_priorities))
                alloted = min(alloted, total_size - accumulated_size)
                accumulated_size += alloted
                assert accumulated_size <= total_size
                min_size = wgt.get_min_size(0, 0)[self.axis]
                if alloted < min_size:
                    del widgets[i]
                    break
                output.append((wgt, alloted))
            else:
                break
        return output[::-1]
    
    @property
    def selected_widget(self):
        if self.selected_index < 0 or self.selected_index >= len(self.visible_widgets):
            return None
        return self.visible_widgets[self.selected_index][0]
    
    def remodel(self, canvas):
        self.visible_widgets = []
        visible_set = set()
        if self.axis == self.HORIZONTAL:
            offx = 0
            for wgt, alloted in self._calc_visible_widgets(canvas.width):
                canvas2 = canvas.subcanvas(offx, 0, alloted, canvas.height)
                wgt.remodel(canvas2)
                self.visible_widgets.append((wgt, (offx, 0, canvas2.width, canvas2.height)))
                visible_set.add(wgt)
                offx += alloted
        else:
            offy = 0
            for wgt, alloted in self._calc_visible_widgets(canvas.height):
                canvas2 = canvas.subcanvas(0, offy, canvas.width, alloted)
                wgt.remodel(canvas2)
                self.visible_widgets.append((wgt, (0, offy, canvas2.width, canvas2.height)))
                visible_set.add(wgt)
                offy += alloted
        
        self.selected_index = 0
    
    def render(self, focused = False, highlight = False):
        for i, (wgt, pos) in enumerate(self.visible_widgets):
            wgt.render(focused = (i == self.selected_index))
    
    def _on_key(self, evt):
        sw = self.selected_widget
        if sw and sw.on_event(evt):
            return True
        elif evt == "ctrl right" and self.selected_index <= len(self.visible_widgets) - 2:
            self.selected_index += 1
        elif evt == "ctrl left" and self.selected_index >= 1:
            self.selected_index -= 1
        return False
    

def HLayout(*widgets):
    return Layout(Layout.HORIZONTAL, widgets)

def VLayout(*widgets):
    return Layout(Layout.VERTICAL, widgets)



if __name__ == "__main__":
    from application import Application
    #te = TextEntry()
    r = HLayout(
        ListBox(SimpleListModel(["hello", "world", "zorld", "kak", "shmak", "flap", "zap"] * 10)),
        ListBox(SimpleListModel(["aaa", "bb", "cccc", "dddddd", "eee", "fffffff", "g"] * 10)),
    )
    app = Application(r)
    app.run(exit = False)


















