""" Device List Widget

This is a Tkinter widget used to display a list of device serial numbers.

"""
#TODO: Move binding to be part of this class
#TODO: Generalize the list manipulation into a support class in util package

import tkinter as tk
from typing import Callable


NO_DEVICE_PRESENT = "<None>"
NO_DEVICE_ASSIGNED = "<Scan barcode> OR <press Return to mark as unused>"

COLOR_SELECTED = 'SlateGray3'
COLOR_NORMAL = 'Gray'
COLOR_FILL_SELECTED = "SlateGray1"
COLOR_FILL_NORMAL = "LightGray"
PAD = 4
ALLOW_WRAPAROUND = False


class DeviceItem(tk.Frame):
    """ Tkinter Widget for inputing and displaying device serial number.

    Args:
        parent (tk.Widget): parent that owns and manages instances of DeviceItem
        device_name (str): Visual display name for given item
        func_select (Callable): Callable function/method to execute when this item is selected
    """
    def __init__(self, parent: tk.Widget, device_name: str, func_select: Callable, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._text = ""
        self._justgotfocus = False
        self._select = func_select

        device_label = tk.Label(self, height=2, text=f'  {device_name}:')
        device_label.pack(side=tk.LEFT, anchor=tk.W, fill=tk.X, expand=False,
                          padx=(PAD,0), pady=PAD)

        self.config(bg=COLOR_NORMAL)
        serialnumber_label = tk.Label(self, height=2, text=NO_DEVICE_ASSIGNED)
        serialnumber_label.pack(fill=tk.X, expand=False, padx=(0,PAD), pady=PAD)

        self.bind("<Button-1>", self._select)
        serialnumber_label.bind("<Button-1>", self._select)
        self._serialnumber_label = serialnumber_label
        self._device_label = device_label

        self.mark(False)


    @property
    def is_set(self):
        """ Boolean indicating if the device has a set value or not

        Returns:
            bool: Does the device have a set, non-default value.
        """
        return self._text != ""


    def mark(self, active):
        """ Visually mark the object as being active or not.

        Args:
            active (bool): used to determine whether or not to visually
                mark the current widget as being active.
        """
        color = COLOR_SELECTED if active else COLOR_NORMAL
        color_fill = COLOR_FILL_SELECTED if active else COLOR_FILL_NORMAL
        self.config(bg=color)
        self._serialnumber_label.config(bg=color_fill)
        self._device_label.config(bg=color_fill)
        if active:
            self._justgotfocus = True


    def handle_keystrokes(self, event: tk.Event):
        """ process incoming keystrokes as inputs for device serial number.

        Args:
            event (tk.Event): keypress event with character information.
        """
        if self._justgotfocus:
            self._text = ""
            self._justgotfocus = False
            
        self._text += event.char
        
        # try:
        #     f = open("vcunumber.txt", "a")
        #     f.write(self._text)
        #     f.close()
        # except Exception as e:
        #     print(e)
        #     pass
        
        self._serialnumber_label.config(text=self._text)


    def accept(self):
        """ Called when user presses enter and will add placeholder text to indicate no device if
        no serial number has been provided.
        """
        if self._text == "":
            self._text = NO_DEVICE_PRESENT
            self._serialnumber_label.config(text=NO_DEVICE_PRESENT)


    def clear(self):
        """ Clear out the serial number value and display a placeholder to inform user to enter
        a value.
        """
        self._text = ""
        self._serialnumber_label.config(text=NO_DEVICE_ASSIGNED)


    @property
    def value(self):
        """ Returns the serial number value.

        Returns:
            str: the devices serial number.
        """
        return self._text if self._text != NO_DEVICE_PRESENT else ""


    def __str__(self):
        return self._text



class DeviceList(tk.Frame):
    """ Tkinter Widget for listing a series of device serial numbers.

    Args:
        parent (tk.Widget): parent widget that contains this device list.
    """
    def __init__(self, parent: tk.Widget, device_count: int, device_term: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._device_count = device_count
        self._device_list = []
        self._selected_index = 0

        for index in range(self._device_count):
            def button_handler(_, i=index):
                self.select(i)

            device_name = f'{device_term} {index+1}' if device_count > 1 else device_term
            item = DeviceItem(self, device_name, button_handler)
            self._device_list.append(item)
            item.pack(fill=tk.X, expand=False, pady=(0,10))

        self.pack(fill=tk.X, expand=False, pady=(0,00))
        self.select(0)


    @property
    def all_set(self) -> bool:
        """ Indicates whether all devices have been given a serial number or intentionally skipped.
        """
        return all((item.is_set for item in self._device_list))


    @property
    def is_last_position(self) -> bool:
        """ Indicates whether the currently selected index is the last in the list.
        """
        return (self._selected_index + 1) == self._device_count


    @property
    def selected_item(self) -> DeviceItem:
        """ Currently selected item in list.
        """
        return self._device_list[self._selected_index]


    @property
    def values(self) -> list[str]:
        """ List of serial numbers for all of the listed devices.
        """
        return [device.value for device in self._device_list]


    def select(self, index: int):
        """ Selects the item with the corresponding index.

        Selected items will be marked with distinguishable highlighting.
        If the index is out or range, coerce to be within the valid range.
        Alternatively, if ALLOW_WRAPAROUND flag is set, use overflowed index to
        wrap around to the opposite end of the range.

        Args:
            index (int): index of device item to select.
        """
        self._mark(self._selected_index, False)

        # Prevent index overflow using either wraparound or coerced strategy
        if ALLOW_WRAPAROUND:
            safe_index = index % self._device_count
        else:
            safe_index = min(self._device_count-1, max(0, index))

        self._selected_index = safe_index
        self._mark(self._selected_index, True)


    def _mark(self, index, active):
        self._device_list[index].mark(active)


    def select_next(self):
        """ Move selection to next item in device list.
        """
        self.select(self._selected_index + 1)


    def select_previous(self):
        """ Move selection to previous item in device list.
        """
        self.select(self._selected_index - 1)


    def handle_keystrokes(self, event: tk.Event):
        """ Forward keystrokes to be handled by the currently selected device item.
        """
        self.selected_item.handle_keystrokes(event)


    def accept(self):
        """ Forwards accept request to currectly selected device item.

        Used when a user hits the <Return> key and checks whether to mark item as vacant or not.
        """
        self.selected_item.accept()


    def clear(self):
        """ Clears out the value for the currently selected device item.
        """
        for device in self._device_list:
            device.clear()
