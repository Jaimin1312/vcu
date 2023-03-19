""" Defines set of resources to be passed between GUI and Controller.
Useful for providing expected interface while maintaining flexibility.
"""
from dataclasses import dataclass

@dataclass
class VCSResources:
    """ Resources provided by GUI for use in VCS testing.
    """
    serial_numbers: str
    enable_transaction_log: bool
    deserializer_lookup: dict
    operator_name: str
    start_time: str
    vcu_number: str
