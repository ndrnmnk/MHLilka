"""Read and return keyboard data for the M5Stack Cardputer."""

from machine import Pin


# lookup values for our keyboard
KC_SHIFT = const(61)
KC_FN = const(65)

KEYCODES = (38, 41, 40, 39, 4, 5, 6, 10, 9, 0)
KEYMAP = {
    38: 'UP',  41: 'DOWN', 40: 'RIGHT', 39: 'LEFT',
    4: 'ENT', 5: 'SPC', 6: 'BSPC', 10: 'ESC', 9: 'TAB', 0: 'G0'
}

MOD_KEYS = const(('ALT', 'CTL', 'FN', 'SHIFT', 'OPT'))
ALWAYS_NEW_KEYS = const(())


class Keys:
    """Keys class is responsible for reading and returning currently pressed keys.

    It is intented to be used by the Input module.
    """

    # optional values set preferred main/secondary action keys:
    main_action = "ENT"
    secondary_action = "SPC"
    aux_action = "G0"

    def __init__(self, **kwargs):  # noqa: ARG002
        self._key_list_buffer = []

        # setup the "G0" button!
        self.G0 = Pin(0, Pin.IN, Pin.PULL_UP)

        # setup column pins. These are read as inputs.
        self.columns = (
            Pin(38, Pin.IN, Pin.PULL_UP),
            Pin(41, Pin.IN, Pin.PULL_UP),
            Pin(40, Pin.IN, Pin.PULL_UP),
            Pin(39, Pin.IN, Pin.PULL_UP),
            Pin(4, Pin.IN, Pin.PULL_UP),
            Pin(5, Pin.IN, Pin.PULL_UP),
            Pin(6, Pin.IN, Pin.PULL_UP),
            Pin(10, Pin.IN, Pin.PULL_UP),
            Pin(9, Pin.IN, Pin.PULL_UP),
            Pin(0, Pin.IN, Pin.PULL_UP),
        )

        self.key_state = []
        
    @staticmethod
    def ext_dir_keys(keylist) -> list:
        """Just for compability with another module"""
        return keylist

    @micropython.viper
    def scan(self):
        """Scan through the matrix to see what keys are pressed."""
        key_list_buffer = []
        self._key_list_buffer = key_list_buffer

        for col_idx, pin in enumerate(self.columns):
            if not pin.value():  # button pressed
                key_list_buffer.append(KEYCODES[col_idx])
        
        return key_list_buffer


    def get_pressed_keys(self, *, force_fn=False, force_shift=False) -> list:
        """Get a readable list of currently held keys."""
        self.scan()
        self.key_state = [KEYMAP[keycode] for keycode in self._key_list_buffer if keycode in KEYMAP]
        return self.key_state


