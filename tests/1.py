import conso


class FiltersBox(conso.Module):
    filters = conso.ModuleAttribute(conso.OList)
    
    def __init__(self):
        self.filters = []
    
    @action(key = "enter")
    def toggle_filter(self):
        pass
    
    @action(key = "del")
    def delete_filter(self):
        pass
    
    @action(key = "space")
    def new_filter(self):
        pass

class BookmarksBox(conso.Module):
    def __init__(self):
        self.bookmarks = []
    
    @action(key = "enter")
    def jump(self):
        pass

class TraceReader(conso.Module):
    def __init__(self):
        self.bookmarks = BookmarksBox()
        self.filters = FiltersBox()
    
    @action(key = "b")
    def add_bookmark(self):
        pass
    
    @action(key = "f")


if __name__ == "__main__":
    conso.Application()










