import itertools
import inspect
import conso
from conso import widgets



class BookmarksModule(widgets.ListModule):
    pass


if __name__ == "__main__":
    r = BookmarksModule(["hello", "world"]*5)
    app = conso.Application(r)
    app.run(exit = False)












