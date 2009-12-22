# 
# press different keys and click the mouse in different places
# "ctrl c" quits
# note that you have to redraw the entire screen after each call to commit()
# but only the parts that were actually changed will be written to 
# the terminal
#
import conso


with conso.Terminal(use_mouse = True, exec_in_tty = True) as term:
    root_canvas = term.get_root_canvas()
    
    while True:
        evt = term.get_event()
        
        if evt == conso.ResizedEvent:
            root_canvas = term.get_root_canvas()
            term.clear_screen()
        elif evt == "ctrl c":
            break
        else:
            root_canvas.write(0, 0, str(evt), fg = "blue", bg = "yellow")
            root_canvas.commit()



