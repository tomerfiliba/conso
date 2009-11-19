import conso
import conso.widgets as cw


root = cw.HLayout(
    cw.Info(
        cw.VLayout(
            cw.Info(
                cw.ListBox(traces_reader),
                priority = 200,
                order = 1,
            ),
            cw.Info(
                cw.TabBox(
                    cw.Frame("function search", None),
                    cw.Frame("time search", None),
                    cw.Frame("add bookmark", None),
                    cw.Frame("add filter", None),
                )
            ),
            cw.Info(
                Label("status line"),
                fixed = True,
                order = 100,
            )
        ),
        order = 1,
    ),
    cw.Info(
        cw.TabBox(
            cw.Frame("Bookmarks", ListBox(bookmarks_list)),
            cw.Frame("Filters", ListBox(filters_list)),
            cw.Frame("Help", None),
        ),
        order = 100,
    ),
)


class Root(Module):
    class MainPanel(Module):
        class TraceReader(Module):
            pass
    
        class BottomPanel(Module):
            class FunctionSearch(Module):
                pass
            
            class TimeSearch(Module):
                pass
            
            class NewBookmark(Module):
                pass
            
            class NewFilter(Module):
                pass
    
    class SidePanel(Module):
        class BookmarksModule(Module):
            pass
        
        class FiltersModule(Module):
            pass
        
        class HelpModule(Module):
            pass
    
        





