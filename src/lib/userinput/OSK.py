import time
from lib.display import Display
from lib.hydra.utils import get_instance

class OnScreenKeyboard:
    def __init__(self):
        self.display = get_instance(Display)
        
        # Define two character sets:
        # base_chars for normal (lowercase) and shift_chars for shifted (uppercase)
        self.base_chars = "abcdefghijklmnopqrstuvwxyz1234567890"
        self.shift_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()"


    def get_text(self, ui):
        DISPLAY_WIDTH = 320
        DISPLAY_HEIGHT = 240
        FONT_HEIGHT = 16

        # sel_index is the current candidate position in the character set.
        sel_index = 0
        # input_text accumulates confirmed characters.
        input_text = ""
        # shift_mode tracks whether the G0 key is active.
        shift_mode = False
        while True:
            # Retrieve new key events.
            keys = ui.get_new_keys()
            if keys:
                for key in keys:
                    if key == 'UP':
                        # Cycle upward in the charset.
                        sel_index = (sel_index - 1) % len(self.base_chars)
                    elif key == 'DOWN':
                        # Cycle downward in the charset.
                        sel_index = (sel_index + 1) % len(self.base_chars)
                    elif key == 'RIGHT':
                        # Append the candidate character to input_text.
                        candidate = self.shift_chars[sel_index] if shift_mode else self.base_chars[sel_index]
                        input_text += candidate
                    elif key == 'BSPC':
                        # Remove the last character.
                        input_text = input_text[:-1]
                    elif key == 'SPC':
                        # Insert a space.
                        input_text += " "
                    elif key == 'ENT':
                        # Clear the line and return the text
                        candidate = self.shift_chars[sel_index] if shift_mode else self.base_chars[sel_index]
                        input_text += candidate
                        self.display.rect(x=0, y=DISPLAY_HEIGHT-FONT_HEIGHT-2, w=DISPLAY_WIDTH, h=FONT_HEIGHT+2, color=self.display.palette[0], fill=True)
                        self.display.show()
                        return self.convert(input_text)
                    elif key == 'ESC':
                        # Clear the input.
                        input_text = ""
                    elif key == 'G0':
                        # Toggle shift mode when G0 is pressed.
                        shift_mode = not shift_mode

            # Determine the candidate character based on the current shift mode.
            candidate = self.shift_chars[sel_index] if shift_mode else self.base_chars[sel_index]

            # Update the display
            self.display.rect(x=0, y=DISPLAY_HEIGHT-FONT_HEIGHT-2, w=DISPLAY_WIDTH, h=FONT_HEIGHT+2, color=self.display.palette[2], fill=True)
            self.display.text(input_text + candidate, 40, DISPLAY_HEIGHT-FONT_HEIGHT, self.display.palette[0])
            self.display.show()

            # Small delay to reduce busy looping.
            time.sleep(0.1)
            
    def convert(self, text):
        res = []
        for c in text:
            if c == ' ':
                res.append('SPC')
            else:
                res.append(c)
        return res
