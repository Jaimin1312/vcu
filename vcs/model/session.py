""" Module for handling test session resources.
Intended to intantiate Session() at the beginning of a test session.
Useful for tracking timing information and common logging details.
"""


from util import timing
from vcs.model import log


class Session():
    """ Used to track timing and log details for a test session.
    """
    def __init__(self):
        self._report = {}
        self.timestamp = None
        self._timer = timing.Timer()


    def start(self):
        """ Starts the session timers.
        """
        self.timestamp = log.get_timestamp()
        self._timer.start()


    def stop(self):
        """ Stops the session timers.
        """
        self._timer.stop()
        self.add_section_details('total time', self._timer.total_in_minutes_and_seconds)
        return self._timer.total_in_minutes_and_seconds


    def add_section_details(self, key, value):
        """ Add a section to the session logs.
        """
        self._report[key] = value


    def get_report(self):
        """ Generate a report of all the logged sections.
        """
        return dict(self._report)
