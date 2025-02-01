import time
import machine
from lib import display, userinput
from lib.hydra import config, popup

# init object for accessing display
DISPLAY = display.Display(use_tiny_buf=True)
INPUT = userinput.UserInput()
CONFIG = config.Config()
overlay = popup.UIOverlay()

# fill background
DISPLAY.fill(CONFIG.palette[2])

# write text to framebuffer
DISPLAY.text(
    text="Hello, World!",
    x=50,
    y=50,
    color=65430,
    )
DISPLAY.show()

overlay.popup_options([["hello", "bye"], ["no", "yes"], ["rufofobia++", "rusofobia+=1", "rusofobia-=-1"]])

