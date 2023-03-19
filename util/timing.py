''' Timing utility module with support for timing tasks with Timer class and writing results to a
    TimeLog file.
'''
import os
import time
import csv


class Timer():
    """ Performance timer for measuring time of system processes.
    """
    def __init__(self):
        self._total_time = 0
        self._start = None


    def start(self):
        """ Starts the timer and zeros out any previously collected total.
        """
        self._total_time = 0
        self._start = time.perf_counter()


    def resume(self):
        """ Restarts the timer, adding on to any previously collected total.
        """
        self._start = time.perf_counter()


    def stop(self):
        """ Stops the timer and returns the current total.

        Returns:
            float: total count collected to this point.
        """
        self._total_time += self._time_since_start
        self._start = None

        return self.total


    @property
    def total(self):
        """ Returns the previously collected total plus any current timer value.

        Returns:
            [type]: [description]
        """
        return self._total_time + self._time_since_start


    @property
    def total_in_minutes_and_seconds(self):
        """ Returns the total timer value in human readible minute and seconds string.

        Returns:
            str: Minutes and seconds written as integers and separated by ":"
        """
        return f'{int(self.total//60)}:{int(self.total%60):02}'


    @property
    def _time_since_start(self):
        running_total = 0
        if self._start:
            stop = time.perf_counter()
            running_total += stop - self._start

        return running_total



class TimeLog():
    """ Supports logging timing values to a file.
    """
    def __init__(self):
        self._names = []
        self._values = []


    def clear(self):
        self._names = []
        self._values = []


    def log(self, name, value):
        self._names.append(name)
        self._values.append(value)


    def write(self, path):
        needs_header = True
        if os.path.exists(path):
            with open(path, 'r', newline='', encoding='utf-8') as fref:
                timelog = csv.DictReader(
                    fref, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                needs_header = timelog.fieldnames != self._names

        with open(path, 'a', newline='', encoding='utf-8') as fref:
            timelog = csv.writer(fref, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if needs_header:
                timelog.writerow(self._names)
            timelog.writerow(self._values)

        # Reset names and values for next log line
        self.clear()
