import conso
from conso.widgets import *


r = VLayout(
    VListBox(SimpleListModel([TextEntry("foo%d" % (i,)) for i in range(30)])),
    Label("helllo world"),
    VListBox(SimpleListModel([TextEntry("foo%d" % (i,)) for i in range(30)])),
    Label("helllo sod"),
)

app = conso.Application(r)
if __name__ == "__main__":
    app.run(exit = False)

