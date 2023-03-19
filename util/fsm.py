""" Support for implementing Finite State Machines.
"""


class State:                                        #pylint: disable=too-few-public-methods
    """ Used to represent labeled states in a state machine
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'{super().__repr__()} - "{self.name}"'

    def __str__(self):
        return self.name


class FSM:
    """ Class used to associate handlers with states for a Finite State Machine.
    """
    def __init__(self):
        self._handlers = {}


    def state_handler(self, state):
        """ Decorator used to mark functions/methods as handlers for given states in the FSM.

        Args:
            state (obj): object for a particular state in the state machine.
        """
        def inner(func):
            def wrapper(*args):
                return func(*args)
            self._handlers.update({state:wrapper})
            return wrapper
        return inner


    @property
    def handlers(self):
        """ Accessor for the handler lookup table

        Returns:
            dict: list of states with associated handlers
        """
        return self._handlers
