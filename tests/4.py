import conso
from conso.widgets import *


class BookmarksList(ListBoxModule):
    @action(title = "Goto", keys = ["enter"])
    def action_goto_selected(self):
        pass

    @action(title = "Rename", keys = ["r"])
    def action_rename_selected(self):
        pass



r = BookmarksList()

app = conso.Application(r)
if __name__ == "__main__":
    app.run(exit = False)

