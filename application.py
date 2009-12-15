from .terminal import Terminal
from .events import ResizedEvent
from .styles import default_style
from .cliapp import CliApplication


class Application(CliApplication):
    def __init__(self, root, style = default_style):
        CliApplication.__init__(self)
        self.root = root
        self.style = style

    def main(self):
        self._mainloop()
        return 0

    def _mainloop(self):
        with Terminal() as term:
            while True:
                evt = term.get_event()
                if evt == ResizedEvent:
                    root_canvas = term.get_root_canvas()
                    self.root.remodel(root_canvas)
                    term.clear_screen()
                elif evt == "ctrl c":
                    break
                else:
                    self.root.on_event(evt)
                self.root.render(self.style, focused = True)
                root_canvas.commit()
            term.clear_screen()





