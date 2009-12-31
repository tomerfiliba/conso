import conso
from conso.widgets import *


r = VLayout(
    Fixed(Label("helllo world"), size = 1),
    Fixed(Label("helllo sod"), size = 1),
)

app = conso.Application(r, capture_mouse = True)
if __name__ == "__main__":
    app.run(exit = False)

