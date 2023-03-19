""" Support for background worker thread of an application.
"""

import threading
import queue


class BackgroundWorkerGeneric(threading.Thread):
    """ Wrapped thread with monitor calls handled in primary thread.

    NOTE: takes in a tkinter frame as it uses the built in .after() method to reschedule the monitor.
    """
    MONITOR_PERIOD = 100

    def __init__(self, frame, update, final, func=None):
        super().__init__()
        self.queue = queue.Queue()
        self.frame = frame
        self.update = update
        self.final = final
        self._func = func


    def run(self):
        """ Placeholder run() method to use for when func is passed in instead of overriden.
        """
        if self._func:
            self._func()


    def start(self):
        super().start()
        self._monitor(self)


    def _monitor(self, thread):
        """ Monitor shared queue for messages while rescheduling the monitor function if thread is alive.

        Args:
            thread (threading.Thread): [description]
        """
        keep_checking = thread.is_alive()

        # Check for messages and pass to update if available
        for _ in range(thread.queue.qsize()):
            try:
                message = thread.queue.get(0)
                self.update(message)
            except queue.Empty:
                pass

        # Reschedule based on whether the thread was still alive at the top of the method
        if keep_checking:
            self.frame.after(self.MONITOR_PERIOD, lambda: self._monitor(thread))
        else:
            thread.final()
