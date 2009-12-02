import conso
from conso.widgets import *


def f(sender):
    raise Exception("hi there")
def g(sender):
    raise Exception("bye there")

#r = ListBox(SimpleListModel(["hello", "world", "zorld", "kak", "shmak"*20, "flap", "zap"] * 10))

r = VLayout(
    LayoutInfo(Frame("foobar"*30,
        #Button("hi", f)
        ProgressBar(70),
    )),
    LayoutInfo(Frame("the list",
        ListBox(SimpleListModel([TextEntry("foo%d" % (i,)) for i in range(30)])),
    )),
    LayoutInfo(HLayout(
        Button("? Help", None),
        Button("Ctrl Q Quit", g),
    )),
    LayoutInfo(TextEntry("moshe")),
    LabelBox(["helllo world"*20] * 20),
)

app = conso.Application(r)
if __name__ == "__main__":
    app.run(exit = False)

