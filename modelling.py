class Model(object):
    pass

class OList(object):
    pass


class TraceReaderModel(Module):
    def __init__(self):
        pass
    
    @action("ctrl b")
    def add_bookmark(self, name):
        pass

class BookmarksModule(Module):
    UI_ATTRS = ["items"]
    
    def __init__(self):
        self.items = OList()
        self.values = {}
    
    @action(key = "enter")
    def jump(self):
        pass

    @action(key = "del")
    def delete(self):
        pass







"""

+--file1.tracer----------------------------------------------------------------+
| -> func1 (1,2,3)                                      ^ +---- bookmarks -----+
| <- 6                                                  | | 1 aaa            ^ |
| -> func2 (2,3,4)                                      | | 2 bbb            | |
|   -> func3 (4,5,6)                   ***              | | 3 ccc            | |
|      -> func4 (6,7,8)                                 | | 4 ddd            | |
|      <- 7                                             | | 5 eee            | |
|   <- 8                                                | | 6 fff            | |
| <- 9                                                  | | 7 ggg            | |
| -> func2 (2,3,4)                                      | | 8 hhh            \/|
|   -> func3 (4,5,6)                                    | |                    |
|      -> func4 (6,7,8)                                 | +----- filters ------+
|      <- 7                                             | | 1                ^ |
|   <- 8                                                | | 2                | |
| <- 9                                                  | | 3                | |
| -> func2 (2,3,4)                                      | | 4                | |
|   -> func3 (4,5,6)                                    | |                  | |
|      -> func4 (6,7,8)                                 | |                  | |
|      <- 7                                             | |                  | |
|   <- 8                                                | |                  | |
| <- 9                                                  \/|                  | |
| --- info liine about selected item -------------------- |                  \/|
+--? help--t time search--s func search--f filter--b bookmark------------------+



+--file1.tracer----------------------------------------------------------------+
| -> func1 (1,2,3)                                      ^ +---- bookmarks -----+
| <- 6                                                  | | 1 aaa            ^ |
| -> func2 (2,3,4)                                      | | 2 bbb            | |
|   -> func3 (4,5,6)                   ***              | | 3 ccc            | |
|      -> func4 (6,7,8)                                 | | 4 ddd            | |
|      <- 7                                             | | 5 eee            | |
|   <- 8                                                | | 6 fff            | |
| <- 9                                                  | | 7 ggg            | |
| -> func2 (2,3,4)                                      | | 8 hhh            \/|
|   -> func3 (4,5,6)                                    | |                    |
|      -> func4 (6,7,8)                                 | +----- filters ------+
|      <- 7                                             | | 1                ^ |
|   <- 8                                                | | 2                | |
| <- 9                                                  | | 3                | |
| -> func2 (2,3,4)                                      | | 4                | |
|   -> func3 (4,5,6)                                    | |                  | |
|      -> func4 (6,7,8)                                 | |                  | |
|      <- 7                                             \/|                  | |
| +--------------search box-----------------------------+ |                  | |
| | function name: foobar_                              | |                  | |
| +-----------------------------------------------------+ |                  \/|
+--? help--t time search--s func search--f filter--b bookmark------------------+



+--file1.tracer----------------------------------------------------------------+
| -> func1 (1,2,3)                                      ^ +---- bookmarks -----+
| <- 6                                                  | | 1 aaa            ^ |
| -> func2 (2,3,4)                                      | | 2 bbb            | |
|   -> func3 (4,5,6)                   ***              | | 3 ccc            | |
|      -> func4 (6,7,8)                                 | | 4 ddd            | |
|      <- 7                                             | | 5 eee            | |
|   <- 8                                                | | 6 fff            | |
| <- 9                                                  | | 7 ggg            | |
| -> func2 (2,3,4)                                      | | 8 hhh            \/|
|   -> func3 (4,5,6)                                    | |                    |
|      -> func4 (6,7,8)                                 | +----- filters ------+
|      <- 7                                             | | 1                ^ |
|   <- 8                                                | | 2                | |
| <- 9                                                  | | 3                | |
| -> func2 (2,3,4)                                      | | 4                | |
|   -> func3 (4,5,6)                                    | |                  | |
|      -> func4 (6,7,8)                                 | |                  | |
|      <- 7                                             \/|                  | |
| +--------------add bookmark---------------------------+ |                  | |
| | name: jjj_                                          | |                  | |
| +-----------------------------------------------------+ |                  \/|
+--? help--t time search--s func search--f filter--b bookmark------------------+



+--file1.tracer----------------------------------------------------------------+
| -> func1 (1,2,3)                                      ^ +---- bookmarks -----+
| <- 6                                                  | | 1 aaa            ^ |
| -> func2 (2,3,4)                                      | | 2 bbb            | |
|   -> func3 (4,5,6)                   ***              | | 3 ccc            | |
|      -> func4 (6,7,8)                                 | | 4 ddd            | |
|      <- 7                                             | | 5 eee            | |
|   <- 8                                                | | 6 fff            | |
| <- 9                                                  | | 7 ggg            | |
| -> func2 (2,3,4)                                      | | 8 hhh            \/|
|   -> func3 (4,5,6)                                    | |                    |
|      -> func4 (6,7,8)                                 | +----- filters ------+
|      <- 7                                             | | 1                ^ |
|   <- 8                                                | | 2                | |
|      <- 7                                             \/| 3                | |
| +--------------help box------------------------------+| | 4                | |
| | xxx yyy zzz                                         | |                  | |
| | xxx yyy zzz                                         | |                  | |
| | xxx yyy zzz                                         | |                  | |
| | xxx yyy zzz                                         | |                  | |
| | xxx yyy zzz                                         | |                  | |
| +-----------------------------------------------------+ |                  \/|
+--? help--t time search--s func search--f filter--b bookmark------------------+


"""













