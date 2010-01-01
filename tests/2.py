import conso
from conso.widgets import *


r = VLayout(
    Fixed(Label("header"), size = 1),
    Fixed(TextEntry("hello world"), size = 1),
    Fixed(Label("footer"), size = 1),
    Fixed(TextEntry("world"), size = 1),
    Fixed(Label("footer2"), size = 1),
    Fixed(TextEntry("world"), size = 1),
    Fixed(Label("footer2"), size = 1),
    Fixed(TextEntry("world"), size = 1),
    Fixed(Label("footer2"), size = 1),
)

app = conso.Application(r, capture_mouse = True)
if __name__ == "__main__":
    app.run(exit = False)

