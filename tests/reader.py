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


class TraceReaderModule(widgets.FramedModule):
    def __init__(self):
        self.bookmarks_mod = BookmarksModule(["hello"] * 30)
        self.filters_mod = FiltersModule(["foobar"] * 30)
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
                widgets.BoundingBox(
                    widgets.VLayout(
                        self.bookmarks_mod,
                        self.filters_mod,
                    ),
                    max_width = 25,
                )
            )
        )

    @widgets.action(title = "Bookmark", keys = ["b"])
    def action_add_bookmark(self, evt):
        return True

    @widgets.action(title = "Filter", keys = ["f"])
    def action_add_filter(self, evt):
        return True

    @widgets.action(title = "Search Function", keys = ["s"])
    def action_search_func(self, evt):
        return True

    @widgets.action(title = "Go to Time", keys = ["g"])
    def action_goto_time(self, evt):
        return True




if __name__ == "__main__":
    r = TraceReaderModule()
    app = conso.Application(r)
    app.run(exit = False)












