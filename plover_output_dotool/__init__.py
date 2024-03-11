import subprocess
import os
from plover.oslayer.keyboardcontrol import KeyboardEmulation as OldKeyboardEmulation
from plover import log


DOTOOL_ENV=os.environ
DOTOOL_ENV["DOTOOL_PIPE"] = "/tmp/plover-dotool"

try:
    from plover.key_combo import parse_key_combo
except ImportError:
    log.warning('with KeyCombo new interface')
    from plover.key_combo import KeyCombo
    _key_combo = KeyCombo()
    def parse_key_combo(combo_string: str):
        return _key_combo.parse(combo_string)

have_output_plugin = False
try:
    from plover.oslayer import KeyboardEmulationBase
    have_output_plugin = True
except ImportError:
    pass

class Main:
    def __init__(self, engine):
        self._engine = engine
        self._old_keyboard_emulation = None
        self._dotoold = None

    def start(self):
        if hasattr(self._engine, "_output"):
            pass
        else:
            if False: # stfu
                log.warning("Output plugin not properly supported!")
            assert self._old_keyboard_emulation is None
            self._old_keyboard_emulation = self._engine._keyboard_emulation
            assert isinstance(self._old_keyboard_emulation, OldKeyboardEmulation)
            self._engine._keyboard_emulation = KeyboardEmulation()
        self._dotoold = subprocess.Popen(["dotoold"], env=DOTOOL_ENV)


    def stop(self):
        if hasattr(self._engine, "_output"):
            log.warning("stop (while Plover has not quited) not supported -- uninstall the plugin instead")
        else:
            assert self._old_keyboard_emulation is not None
            self._engine._keyboard_emulation = self._old_keyboard_emulation
            self._old_keyboard_emulation = None
        self._dotoold.send_signal(15) # SIGTERM

mods = {
    'alt_l': 'k:56', 'alt_r': 'k:100',
    'control_l': 'k:29', 'control_r': 'k:97',
    'shift_l': 'k:42', 'shift_r': 'k:54',
    'super_l': 'k:125', 'super_r': 'k:126',
}

class KeyboardEmulation(*([KeyboardEmulationBase] if have_output_plugin else [])):
    """Emulate keyboard events."""

    @classmethod
    def get_option_info(cls):
        return {}

    def __init__(self, params = None):
        if have_output_plugin:
            KeyboardEmulationBase.__init__(self, params)
        self._ms = None

    def start(self):
        start()

    def cancel(self):
        pass

    def set_ms(self, ms):
        if self._ms != ms:
            self._ms = ms

    def _dotool(self, inp):
        print(inp)
        with open(DOTOOL_ENV["DOTOOL_PIPE"], 'w') as file:
            file.write(inp + "\n")
            file.flush()
            file.close()

    def _dotool_string(self, s):
        self._dotool("type " + s)

    def send_string(self, s):
        self._dotool_string(s)

    def send_key_combination(self, combo_string):
        print(combo_string)
        key_events = parse_key_combo(combo_string)
        print(key_events)

        # Split key_events into release list and press list
        for (key, pressed) in key_events:
            k = (mods[key] if key in mods else key)
            arg = "keydown " if pressed else "keyup "
            # Send keyup and then keydown to avoid clashes
            self._dotool(arg + k)



    def send_backspaces(self, n):
        self._dotool_string("\b" * n)
