import conso
from conso.widgets import *


r = VLayout(
    VListBox(SimpleListModel([TextEntry("foo%d" % (i,)) for i in range(30)])),
    Label("helllo world"),
    HListBox(SimpleListModel([Label("foo%d" % (i,)) for i in range(30)])),
    Label("helllo sod"),
)
#r = HListBox(
#    SimpleListModel([Button("foo%d" % (i,), None) for i in range(30)]), 
#    auto_focus = True
#)

app = conso.Application(r)
if __name__ == "__main__":
    app.run(exit = False)

