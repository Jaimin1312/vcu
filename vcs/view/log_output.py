''' Module provides Tk widget for visualizing output log '''
import tkinter as tk

from util.gui import add_scrollbar


class LogOutput():
    """ Tk Widget for displaying log information in a scollable frame.

    Args:
        tk (Frame): parent frame/object
    """
    def __init__(self, parent):
        self.frame = tk.Frame(parent, width=100)

        self._output = add_scrollbar(
            tk.Text(self.frame, state=tk.DISABLED, relief=tk.FLAT, highlightbackground='grey',
                    highlightthickness=1, bd=0, fg='black'))
        self._output.pack(fill=tk.BOTH, expand=True)


    def insert(self, message, newline=True):
        """ Inserts text into the logged output buffer.

            NOTE: the output Text element must have it's state configured to allow for the
            additional text, and then changed back to prevent the user from altering the
            text.
        Args:
            message (str): Text to add to the output display buffer.
            newline (bool, optional): If enabled, adds a newline to the message.
                Can be disabled to allow for custom manipulation of the buffer.
                Defaults to True.
        """
        if newline:
            message += '\n'
        self._output.config(state=tk.NORMAL)
        self._output.insert(tk.END, message)
        self._output.yview_moveto(1)
        self._output.config(state=tk.DISABLED)


    def clear(self):
        """ Clears the contents of the widget.
        """
        self._output.config(state=tk.NORMAL)
        self._output.delete('1.0', tk.END)
        self._output.config(state=tk.DISABLED)
