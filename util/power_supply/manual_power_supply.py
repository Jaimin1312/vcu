""" Placeholder power module to prompt user to manually configure the power supply.
"""

import ctypes

MB_STYLES_OK = 0
MB_STYLES_OK_CANCEL = 1
MB_STYLES_ABORT_RETRY_IGNORE = 2
MB_STYLES_YES_NO_CANCEL = 3
MB_STYLES_YES_NO = 4
MB_STYLES_RETRY_CANCEL = 5
MB_STYLES_CANCEL_TRYAGAIN_CONTINUE = 6


def MessageBox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


class Power:
    def __init__(self):
        self._voltage = 0.0
        self._current = 0.0
        pass

    def set_voltage(self, voltage):
        self._voltage = voltage

    def set_current_limit(self, amps):
        self._current = amps

    def enable(self):
        MessageBox(
            "Enable Power Supply",
            f"Turn on the power supply to {self._voltage}V with {self._current}A limit",
            MB_STYLES_OK,
        )

    def disable(self):
        MessageBox(
            "Disable Power Supply",
            "Turn off the power supply",
            MB_STYLES_OK,
        )

    def close(self):
        pass

def open():
    return Power()
