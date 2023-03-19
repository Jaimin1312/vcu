''' Main UI layout for camera and vcu test applications.
'''
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from util.gui import StatusBar
from vcs.model import application
from vcs.control.controller import ExecutorController
from vcs.model.bgstates import BGStates
from vcs.model.resources import VCSResources
from vcs.view.camera_grid import CameraGrid
from vcs.view.device_list import DeviceList
from vcs.view.log_output import LogOutput
from vcs.view.operator import OperatorItem

import datetime
import os
import shutil

class MainLayout(tk.Frame):
    """ Camera/VCU test application GUI (tkinter).
    """
    def __init__(self, root, mapper):
        super().__init__(root)
        self.controller: ExecutorController = None

        self._mapper = mapper

        # Initialize GUI and then start main event loop
        self._setup_menu(root)
        self._setup_ui_elements(self._mapper.device_count, self._mapper.device_term)
        self._setup_bindings(root)


    def _setup_menu(self, root):
        menubar = tk.Menu(root)

        filemenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open Logging Directory",
                             command=self._cmd_open_logging_dir)
        filemenu.add_command(label="Update Baseline Images",
                             command=self._cmd_update_baseline_images)

        root.config(menu=menubar)


    def _setup_ui_elements(self, device_count, device_term):
        """ Assemble and configure elements to make up primary user interface
        """
        # Create layout containers
        outer_frame = tk.Frame(self, relief=tk.SUNKEN, bd=2)
        right_frame = tk.Frame(outer_frame)
        left_frame = tk.Frame(outer_frame)
        bottom_bar = tk.Frame(self, bg='yellow')
        button_bar = tk.Frame(right_frame)

        # Create elements
        self._camera_grid = CameraGrid(left_frame)
        self._device_list = DeviceList(right_frame, device_count, device_term)
        self._operator_label = OperatorItem(right_frame)
        self._step_count = 0

        input_operator_name = tk.Entry(right_frame)
        input_operator_name.pack(fill=tk.X, padx=(0, 0), pady=(0, 10))
        self._input_operator_name=input_operator_name

        self._start_button = ttk.Button(
            button_bar, text="Start", command=self._check_for_start, width=20)
        self._log_output = LogOutput(right_frame)
        self._status_bar = StatusBar(bottom_bar)

        # Setup layout for elements
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        outer_frame.pack(fill=tk.BOTH, expand=True)
        right_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=10, pady=(10,10))
        left_frame.pack(fill=tk.BOTH, side=tk.LEFT)#, expand=True, padx=10, pady=(10,10))

        self._status_bar.pack(fill=tk.BOTH)
        button_bar.pack(fill=tk.X, padx=(0, 0), pady=(0, 10))
        self._log_output.frame.pack(fill=tk.BOTH, expand=True)
        self._start_button.pack(anchor=tk.E, padx=(0,0), pady=(0, 0))
        self.pack(expand=True, fill=tk.BOTH)


    def _setup_bindings(self, root):
        """ Setup the key and mouse
        """
        root.bind("<Tab>", lambda event: self._device_list.select_next())
        root.bind("<Shift-Tab>", lambda event: self._device_list.select_previous())
        root.bind("<Return>", self._handle_return_key)
        root.bind("<BackSpace>", lambda event: (self._device_list.selected_item.clear(),
                                                self._device_list.select_previous()))
        root.bind("<Delete>", lambda event: (self._device_list.selected_item.clear(),
                                             self._device_list.select_next()))
        root.bind("<Up>", lambda event: self._device_list.select_previous())
        root.bind("<Down>", lambda event: self._device_list.select_next())
        #root.bind("<KeyPress>", self._device_list.handle_keystrokes)
        for numeral in range(10):
            root.bind(f"{numeral}", self._device_list.handle_keystrokes)
        root.bind("<space>", self._device_list.handle_keystrokes)
        root.bind("-", self._device_list.handle_keystrokes)
        root.bind("_", self._device_list.handle_keystrokes)

        self.focus()


    def _handle_return_key(self, _):
        self._device_list.accept()
        if self._device_list.all_set and self._device_list.is_last_position:
            self._check_for_start()
        else:
            self._device_list.select_next()


    def _check_for_start(self):
        response = tk.messagebox.askyesno(
            "Check for start", "All positions have been assigned.\nStart the test?", default='no')
        if response:
            # Load in latest settings and then save merged values
            self._start_time = str(datetime.datetime.now().strftime('%Y-%m-%d T%H:%M:%S'))           
            application.settings.load()
            application.settings.save()
            VCU_NUMBER = ""
            try:
                f = open("vcunumber.txt", "r")
                VCU_NUMBER = f.read() 
                f.close()

                os.remove('vcunumber.txt')
            except Exception as e:
                pass
     
            if VCU_NUMBER != "":
                self.controller.start(
                    VCSResources(
                        vcu_number=VCU_NUMBER,
                        start_time = self._start_time,
                        operator_name = self._input_operator_name.get(),
                        serial_numbers = self._mapper.get_serial_numbers(self._device_list.values),
                        enable_transaction_log = self._mapper.enable_transaction_log,
                        deserializer_lookup = self._mapper.get_deserializer_lookup(),
                    )
                )
            else:
                tk.messagebox.showerror('Error','VCU NUMBER can not be empty!')



    def _cmd_open_logging_dir(self):
        self.controller.open_logging_dir()


    def _cmd_update_baseline_images(self):
        # Open dialog to have user select a directory to use as the new baseline image
        path = filedialog.askdirectory(
            title="Select a directory for new baseline images",
            initialdir=application.settings.values.logging_path,
        )
        self.controller.update_baseline_images(path)


    def _ask_user(self, header, message):
        response = tk.messagebox.askyesno(header, message)
        self.controller.resume(response)


    def _prompt_user(self, header, message):
        response = tk.messagebox.askokcancel(header, message)
        self.controller.resume(response)


    def reset_handler(self):
        """ Reset the UI to a known state based on the condition of the background operation.
        """
        self._log_output.insert('Background worker finalized')


    def update_handler(self, message: dict):
        """ Handle messages from the controller.

        Args:
            message (dict): dictionary of named messages.

        Raises:
            NotImplementedError: Raised if an unknown message key is receiving from the controller.
        """
        for key, value in message.items():
            if key == 'state':
                self._status_bar.set(f'{value}')
                if value is BGStates.SETUP:
                    self._log_output.clear()
                    self._camera_grid.clear()
                    self._log_output.insert(f'Operator Name: {str(self._input_operator_name.get())}',True)
                    self._log_output.insert(f'Start Time: {str(self._start_time)}',True)
                if value is BGStates.CLEANUP:
                    self._device_list.clear()
                    self._device_list.select(0)
                    self.focus()
                if value is not BGStates.IDLE:
                    self._step_count = self._step_count + 1
                    self._log_output.insert(f"")
                    self._log_output.insert(f"---------------- STEP {self._step_count} ----------------")
                    self._log_output.insert(f"------------------------------------------")
                    self._log_output.insert(f"")
                    self._log_output.insert(f'Step: {value}')      
            elif key == 'msg':
                self._log_output.insert(value[0], newline=value[1])
            elif key == 'ask':
                statement, question = value
                self._ask_user(statement, question)
            elif key == 'prompt':
                statement, question = value
                self._prompt_user(statement, question)
            elif key == 'cameras':
                self._camera_grid.set(value)
            elif key == 'pass':
                self._camera_grid.mark_as_pass(value)
            elif key == 'fail':
                self._camera_grid.mark_as_fail(value)
            else:
                raise NotImplementedError(f'Support for {key} not implemented yet!')
