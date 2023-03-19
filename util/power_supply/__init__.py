""" Provides common import layer for various power supplies.
"""
from . import bk_power_supply
#from . import ametek_power_supply
#from . import sorensen_power_supply
from . import manual_power_supply
from .errors import NotDetected, NoSupply, MultipleSupplies


def detect():
    """ Opens the first available power supply.

        COM port detected automatically
    """
    supplies = bk_power_supply.open() #or ametek_power_supply.open() or sorensen_power_supply.open()
    if not supplies:
        raise NoSupply()

    return supplies
