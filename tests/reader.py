import conso
from conso import widgets



class BookmarksModule(widgets.ListModule):
    @widgets.action(title = "Jump", keys = ["enter"])
    def action_jump_selected(self, evt):
        return True

    @widgets.action(title = "Edit", keys = ["e"])
    def action_edit_selected(self, evt):
        return True


class FiltersModule(widgets.ListModule):
    @widgets.action(title = "Toggle", keys = ["t"])
    def action_toggle_selected(self, evt):
        return True

    @widgets.action(title = "Edit", keys = ["e"])
    def action_edit_selected(self, evt):
        return True


class InputModule(widgets.FramedModule):
    def __init__(self, message, text = ""):
        self.text = TextEntry(text)
        widgets.FramedModule.__init__(self,
            VLayout(Label(message), self.text)
        )

class FunctionSearch(InputModule):
    def __init__(self):
        InputModule.__init__(self, "Enter function name (may be partial)")
    
    @widgets.action(title = "Forward", keys = ["enter", "f"])
    def action_search_fwd(self, evt):
        pass

    @widgets.action(title = "Backward", keys = ["shift enter", "b"])
    def action_search_fwd(self, evt):
        pass


class TimeSearch(InputModule):
    def __init__(self):
        InputModule.__init__(self, "Enter time ([dd:]hh:mm:ss)")
    
    @widgets.action(title = "Jump", keys = ["enter", "ctrl j"])
    def action_goto_time(self, evt):
        pass


class TraceReaderModule(widgets.FramedModule):
    def __init__(self):
        self.bookmarks_mod = BookmarksModule([widgets.TextEntry("hello%d" % i) for i in range(30)])
        self.filters_mod = FiltersModule([widgets.TextEntry("foobar%d" % i) for i in range(30)])
        widgets.FramedModule.__init__(self,
            widgets.HLayout(
                widgets.LayoutInfo(
                    widgets.Frame(
                        widgets.VListBox(
                            widgets.SimpleListModel(["trace"*20]*100),
                            allow_scroll = True,
                        ),
                        title = "Traces"
                    ),
                ),
                widgets.VLayout(
                    self.bookmarks_mod,
                    self.filters_mod,
                ),
            )
        )

    @widgets.action(title = "Add Bookmark", keys = ["b"])
    def action_add_bookmark(self, evt):
        return True

    @widgets.action(title = "Add Filter", keys = ["f"])
    def action_add_filter(self, evt):
        return True

    @widgets.action(title = "Search Function", keys = ["s"])
    def action_search_func(self, evt):
        return True

    @widgets.action(title = "Go to Time", keys = ["g"])
    def action_goto_time(self, evt):
        return True
    
    @widgets.action(keys = ["ctrl b"])
    def action_select_bookmarks_module(self, evt):
        pass

    @widgets.action(keys = ["ctrl f"])
    def action_select_filters_module(self, evt):
        pass





if __name__ == "__main__":
    r = TraceReaderModule()
    app = conso.Application(r, capture_mouse = True)
    app.run(exit = False)












