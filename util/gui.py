""" Generic Tkinter elements used to create graphical user interfaces.
"""
import ctypes
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from idlelib.tooltip import Hovertip

from util.path import get_path_relative_to_application


def set_state(parent, state):
    if parent.winfo_class() not in ('TFrame', 'TLabelframe', 'Frame', 'Labelframe'):
        parent.configure(state=state)
    else:
        for child in parent.winfo_children():
            set_state(child, state)


def add_scrollbar(element):
    """ Adds a scrollbar to a tkinter element.
    NOTE: this only appears to be valid for certain tkinter types.
        For Scrollbars, used the ScrollableFrame instead.

    Args:
        element (tkinter element): tkinter element to attach scrollbar to

    Returns:
        tkinter element: element with added scrollbar.  Acts as a pass-through for chaining together additions.
    """
    vscroll = tk.Scrollbar(element)
    element.config(yscrollcommand=vscroll.set)

    # Configure the scroll bar to update the Text box
    vscroll.config(command=element.yview)
    vscroll.pack(side=tk.RIGHT, fill=tk.Y)

    return element


class ScrollableFrame(tk.Frame):
    """ Tkinter frame with vertical scrollbar to scroll any child content.
    Intended to be a reusable component.
    """
    def __init__(self, parent):
        super().__init__(parent)

        canvas = tk.Canvas(self, bd=0, highlightthickness=0, borderwidth=0)
        self.inner = tk.Frame(canvas)

        vscroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        # Pack elements
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner_id = canvas.create_window(0, 0, window=self.inner, anchor=tk.NW, tags='self.inner')

        # Setup bindings to auto-reconfigure
        def _config_inner(_):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.inner.bind('<Configure>', _config_inner)

        def _config_canvas(_):
            if self.inner.winfo_reqwidth() != canvas.winfo_width():
                canvas.itemconfigure(inner_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _config_canvas)


class Indicator(tk.Canvas):
    """ Visual indicator that can display boolean states.

    Supports alternate visual styles:
        rect = Rectangular indicator
        circ = Oval indicator

    """
    STYLE_RECT = 'rect'
    STYLE_CIRC = 'circ'
    def __init__(
        self, *args, on_color='lightgreen', off_color='grey',
        on_text='ON', off_text='OFF', style=STYLE_RECT, **kwargs
        ):
        super().__init__(*args, **kwargs)

        self._on_text = on_text
        self._off_text = off_text
        width=kwargs['width']
        height=kwargs['height']

        if style == Indicator.STYLE_RECT:
            self.create_rectangle(0,0,width,height, fill=on_color, tags='on')
            self.create_rectangle(0,0,width,height, fill=off_color, tags='off')
        elif style == Indicator.STYLE_CIRC:
            self.create_oval(0,0,width,height, fill=on_color, tags='on')
            self.create_oval(0,0,width,height, fill=off_color, tags='off')
        else:
            raise NotImplementedError(f'No support for "{style}"')

        self._tip = Hovertip(self, self._off_text)


    def set(self, value):
        if value:
            self.enable()
        else:
            self.disable()


    def enable(self):
        self.tag_raise('on', 'off')
        self._tip.text = self._on_text


    def disable(self):
        self.tag_raise('off', 'on')
        self._tip.text = self._off_text


class LabeledElement(tk.Frame):
    """ Adds a label to a tkinter element.
    """
    def __init__(self, name, element, parent, *args, **kwargs):
        super().__init__(parent)

        self.name = name
        self._label = tk.Label(self, anchor='w', text=self.name)
        self._element = element(self, *args, **kwargs)

        self._label.pack(expand=1, fill=tk.X, side=tk.LEFT)
        self._element.pack(expand=1, fill=tk.X, side=tk.RIGHT)


class StatusBar(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._status = tk.StringVar()
        self._label = tk.Label(self, textvariable=self._status)

        self._label.pack(side=tk.LEFT)

    def set(self, message):
        self._status.set(message)


class DirectorySelector(tk.Frame):
    def __init__(self, *args, target, command=None, **kwargs):
        super().__init__(*args, pady=2, padx=2, **kwargs)

        self._target = tk.StringVar()
        self._target.set(target)
        if command:
            self._command = command
        else:
            self._command = lambda path: ()

        self._pathbox = ttk.Entry(self, textvariable=self._target, state="readonly")
        self._button_select_path = ttk.Button(self, width=3, text='...', command=self._select)

        self._pathbox.pack(ipady=4, side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._button_select_path.place(relx=1.0, rely=0.5, x=-2, y=-1, anchor=tk.E)


    def _select(self):
        target = filedialog.askdirectory(initialdir=self._target.get())
        if target:
            self._target.set(target)
            self._command(target)


    @property
    def target(self):
        return self._target.get()



class SearchBar(tk.Frame):
    """ Search bar with built in support for advanced searching by providing hints and context.

    Args:
        tk ([type]): [description]
    """
    def __init__(self, *args, command=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._list = []
        if command:
            self._command = command
        else:
            self._command = lambda path: ()

        # Setup elements and layout
        self._entry = ttk.Entry(self)
        self._listbox = tk.Listbox(self)
        self._entry.pack(ipady=4, fill=tk.BOTH, expand=True)
        self._entry.bind('<KeyRelease>', self._scankey)
        self._entry.bind('<Escape>', self._reset)
        self._entry.bind('<Return>', self._search)

        style = ttk.Style()
        #style.theme_use('clam')
        style.configure('my.TButton', font=('Segoe UI Symbol', 10), borderwidth=0)
        self._searchbutton = ttk.Button(self, width=3, text='', style='my.TButton', command=self._search)
        self._resetbutton = ttk.Button(self, width=3, text='', style='my.TButton', command=self._reset)

        self._reset()


    def _scankey(self, event):
        val = event.widget.get()
        if val == "":
            data = self._list
        else:
            data = []
            for item in self._list:
                if val.lower() in item.lower():
                    data.append(item)
        self._update(data)


    def _update(self, data):
        self._listbox.delete(0, 'end')
        for item in data:
            self._listbox.insert('end', item)


    def _reset(self, event=None):
        self._searchbutton.place(relx=1.0, rely=0.5, x=-2, y=-1, anchor=tk.E)
        self._resetbutton.place_forget()
        self._entry.delete(0, 'end')
        self._update('')
        self._command('')


    def _search(self, event=None):
        self._searchbutton.place_forget()
        self._resetbutton.place(relx=1.0, rely=0.5, x=-2, y=-1, anchor=tk.E)
        value = self._entry.get()
        self._command(value)


def treeview_sort_column(treeview, col, reverse):
    children = [(treeview.set(k, col), k) for k in treeview.get_children('')]
    children.sort(reverse=reverse)

    # rearrange items in sorted positions
    for index, (_, k) in enumerate(children):
        treeview.move(k, '', index)

    # reverse sort next time
    treeview.heading(col, command=lambda: treeview_sort_column(treeview, col, not reverse))


#TODO: fix description
class AppTemplate():
    """ Configures the application with various window properties.

    Args:
        root (tk.Tk): _description_
        title (str): _description_
        dimensions (tuple): _description_
        icon_path (str): _description_
        is_zoomed (bool, optional): _description_. Defaults to True.
        is_topmost (bool, optional): _description_. Defaults to False.
        is_toolwindow (bool, optional): _description_. Defaults to False.
        is_fullscreen (bool, optional): _description_. Defaults to False.
        transparency_color (str, optional): _description_. Defaults to None.
    """
    def __init__(self, title: str, dimensions: tuple, icon_path: str,
                 is_zoomed=True, is_topmost=False, is_toolwindow=False,
                 is_fullscreen=False, transparency_color=None):
        root = tk.Tk()
        self.root = root

        # Set the DPI awareness to PROCESS_PER_MONITOR_DPI_AWARE to fix the issue with tkinter
        #   text looking blurry.
        # See:
        #   https://docs.microsoft.com/en-us/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness    #pylint: disable=line-too-long
        #   https://stackoverflow.com/questions/68700679/how-to-stop-text-in-tkinter-from-appearing-blurry-pixelated        #pylint: disable=line-too-long
        ctypes.windll.shcore.SetProcessDpiAwareness(2)

        # Set initial application size and window state
        root.geometry('{}x{}'.format(*dimensions))
        if is_zoomed:
            # Causes the window to be the same size as the screen without being fullscreen.
            root.state('zoomed')
        root.attributes('-toolwindow', is_toolwindow)

        # Setup fullscreen support (F11 to toggle, ESC to exit, initial state set by global)
        root.attributes('-fullscreen', is_fullscreen)
        root.bind("<F11>", lambda event: root.attributes("-fullscreen",
                                                            not root.attributes("-fullscreen")))
        root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

        root.attributes('-topmost', is_topmost)
        if icon_path:
            icon_path = get_path_relative_to_application(icon_path)
            root.iconbitmap(icon_path)
        root.title(title)

        # Set up a color to be fully transparent, meaning it will look to the underlying desktop
        if transparency_color:
            root.wm_attributes('-transparentcolor', transparency_color)
