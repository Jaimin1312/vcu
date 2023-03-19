""" Device List Widget

This is a Tkinter widget used to display a list of device serial numbers.

"""
#TODO: Move binding to be part of this class
#TODO: Generalize the list manipulation into a support class in util package

import tkinter as tk
from typing import Callable

OPERATOR_NAME = "Operator Name"

COLOR_SELECTED = 'SlateGray3'
COLOR_NORMAL = 'Gray'
COLOR_FILL_SELECTED = "SlateGray1"
COLOR_FILL_NORMAL = "LightGray"
PAD = 4
ALLOW_WRAPAROUND = False


class OperatorItem(tk.Frame):

    def __init__(self, parent: tk.Widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._text = ""
        self._justgotfocus = False

        self.config(bg=COLOR_NORMAL)
        operator_label = tk.Label(self, height=2, text=OPERATOR_NAME)
        operator_label.pack(fill=tk.X, padx=(4,4), pady=4)
        
        self._operator_label = operator_label
        self.mark(True)
        self.pack(fill=tk.X, expand=False, pady=(0,10))


    @property
    def is_set(self):
        
        return self._text != ""


    def mark(self, active):
      
        color = COLOR_SELECTED if active else COLOR_NORMAL
        color_fill = COLOR_FILL_SELECTED if active else COLOR_FILL_NORMAL
        self.config(bg=color)
        self._operator_label.config(bg=color_fill)

        if active:
            self._justgotfocus = True


    def handle_keystrokes(self, event: tk.Event):
       
        if self._justgotfocus:
            self._text = ""
            self._justgotfocus = False
        self._text += event.char
        self._operator_label.config(text=self._text)


    def accept(self):
     
        if self._text == "":
            self._text = OPERATOR_NAME
            self._operator_label.config(text=OPERATOR_NAME)


    def clear(self):
       
        self._text = ""
        self._operator_label.config(text=OPERATOR_NAME)


    @property
    def value(self):
     
        return self._text if self._text != OPERATOR_NAME else ""


    def __str__(self):
        return self._text


