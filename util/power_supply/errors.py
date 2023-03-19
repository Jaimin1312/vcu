""" Custom Exception definitions related to power supplies on a system.
"""

class NotDetected(Exception):
    """ Used to indicate that a power supply has not been detected on the speficied COM port.
    """
    def __init__(self, port_name):
        super().__init__()
        self.port_name = port_name

    def __str__(self):
        return "No power supply was not detected on " + self.port_name + "."

class NoSupply(Exception):
    """ Used to indicate that no power supplies have been detected on the system. """
    def __str__(self):
        return "There must be exactly one Ametek or BK Precision 1685B power supply attached. None was found."              #pylint: disable=line-too-long

class MultipleSupplies(Exception):
    """ Used to indicate that more than one power supply has been detected on the system. """
    def __str__(self):
        return "There must be exactly one Ametek or BK Precision 1685B power supply attached. More than one was found."     #pylint: disable=line-too-long
