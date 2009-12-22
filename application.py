from .terminal import Terminal
from .events import ResizedEvent, KeyEvent
from .styles import default_style
from .cliapp import CliApplication


class Application(CliApplication):
    def __init__(self, root, style = default_style, capture_mouse = False, exec_in_tty = True, force_quit_key = "ctrl c"):
        CliApplication.__init__(self)
        self.root = root
        self.style = style
        self.exec_in_tty = exec_in_tty
        self.capture_mouse = capture_mouse
        self.force_quit_key = KeyEvent.from_string(force_quit_key)

    def main(self):
        self._mainloop()
        return 0

    def _mainloop(self):
        with Terminal(use_mouse = self.capture_mouse, exec_in_tty = self.exec_in_tty) as term:
            redraw = True
            while True:
                evt = term.get_event()
                if evt == ResizedEvent:
                    root_canvas = term.get_root_canvas()
                    self.root.remodel(root_canvas)
                    term.clear_screen()
                    redraw = True
                elif evt == self.force_quit_key:
                    break
                elif self.root.on_event(evt):
                    redraw = True
                
                if redraw:
                    self.root.render(self.style, focused = True)
                    root_canvas.commit()
                    redraw = False
            
            term.clear_screen()





