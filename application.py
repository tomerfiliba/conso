from .terminal import Terminal
from .events import ResizedEvent, KeyEvent
from .styles import default_style
from .cliapp import CliApplication


class Application(CliApplication):
    FORCE_QUIT_KEY = "ctrl c"
    CAPTURE_MOUSE = False
    EXEC_IN_TTY = True
    
    def __init__(self, root, style = default_style):
        CliApplication.__init__(self)
        self.root = root
        self.style = style
        self.FORCE_QUIT_KEY = KeyEvent.from_string(self.FORCE_QUIT_KEY)

    def main(self):
        self._mainloop()
        return 0

    def _mainloop(self):
        with Terminal(use_mouse = self.CAPTURE_MOUSE, exec_in_tty = self.EXEC_IN_TTY) as term:
            while True:
                evt = term.get_event()
                if evt == ResizedEvent:
                    root_canvas = term.get_root_canvas()
                    self.root.remodel(root_canvas)
                    term.clear_screen()
                elif evt == self.FORCE_QUIT_KEY:
                    break
                else:
                    self.root.on_event(evt)
                self.root.render(self.style, focused = True)
                root_canvas.commit()
            term.clear_screen()





