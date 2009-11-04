import sys
import urwid
import urwid.curses_display


class Application(object):
    PALETTE = {}
    
    def __init__(self):
        self.view = None
    
    def main(self):
        self.active = True
        self.ui = urwid.curses_display.Screen()
        self.ui.register_palette([(k,) + tuple(v) for k, v in self.PALETTE.iteritems()])
        self.ui.run_wrapper(self._mainloop)
    
    def _mainloop(self):
        dims = self.ui.get_cols_rows()
        while self.active:
            canvas = self.view.render(dims)
            self.ui.draw_screen(dims, canvas)
            try:
                keys = self.ui.get_input()
            except KeyboardInterrupt:
                self.active = False
                continue
            for key in keys:
                if key == "window resize":
                    dims = self.ui.get_cols_rows()
                else:
                    self.view.handleKey(key)

class TraceReader(Application):
    view = 8


class TraceTree(Interactive):
    @action(key = "down")
    def cursor_down(self):
        pass
    
class BookmarksFrame(InteractiveList):
    def __init__(self):
        self.items = InteractiveList()
    
    @action(key = "enter")
    def jump_bookmark(self):
        pass








if __name__ == "__main__":
    def run_in_tty():
        if not sys.stdout.isatty():
            import subprocess
            p = subprocess.Popen(["/usr/bin/gnome-terminal", "-t", "python shell", 
                "-x", "/usr/bin/python", "-i", __file__] + sys.argv[1:])
            rc = p.wait()
            sys.exit(rc)
    run_in_tty()
    
    TraceReader().main()




