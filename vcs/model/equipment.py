''' Module to support organizing the system equipment.
'''
from util import power_supply
from vcs.model.resources import VCSResources
from vcs.model.vcu import VCU
from vcs.model.camera import Camera

import time

#VOLTAGE = 46.5
#CURRENT_LIMIT = 1
VOLTAGE = [12.0, 5.0, 3.3]
CURRENT_LIMIT = [1.5, 3.0, 3.0]


class Equipment:                                            #pylint: disable=too-few-public-methods
    """ Collection of all system equipment.
    """
    def __init__(self, resources: VCSResources, vcu):
        self.resources = resources
        self._power_supplies = []   # None  #: list[Power] = []
        self.vcu: VCU = vcu
        self.camera_list = [Camera(index, serial_number) for index, serial_number in \
            enumerate(self.resources.serial_numbers)]


    def setup(self):
        """ Make connections to system equipment.
        """
        if not self._power_supplies:    # is None:
            try:
                self._power_supplies = power_supply.detect()
            except power_supply.NoSupply:
                self._power_supplies = power_supply.manual_power_supply.open()


    def enable_supply(self):
        """ Set the expected voltage and current limits and then enable the power supply.
        """
#        for i in range(0, len(self._power_supplies)):
#            self._power_supplies[i].set_voltage(VOLTAGE[i])
#            self._power_supplies[i].set_current_limit(CURRENT_LIMIT[i])
#            self._power_supplies[i].enable()
        for i in range(0, len(self._power_supplies)):
#            with self._power_supplies[i] as ps:
#                ps.set_channel(0)
#                ps.apply_v_and_i(VOLTAGE[0], CURRENT_LIMIT[0])
#                time.sleep(500e-3)
#                ps.set_channel(1)
#                ps.apply_v_and_i(VOLTAGE[1], CURRENT_LIMIT[1])
#                time.sleep(100e-6)
#                ps.set_channel(2)
#                ps.apply_v_and_i(VOLTAGE[2], CURRENT_LIMIT[2])
            self._power_supplies[i].set_channel(0)
            self._power_supplies[i].apply_v_and_i(VOLTAGE[0], CURRENT_LIMIT[0])
            self._power_supplies[i].enable()
            time.sleep(500e-3)
            self._power_supplies[i].set_channel(1)
            self._power_supplies[i].apply_v_and_i(VOLTAGE[1], CURRENT_LIMIT[1])
            self._power_supplies[i].enable()
            time.sleep(100e-6)
            self._power_supplies[i].set_channel(2)
            self._power_supplies[i].apply_v_and_i(VOLTAGE[2], CURRENT_LIMIT[2])
            self._power_supplies[i].enable()


    def cleanup(self):
        """ Places equipment back into known state.

        Disables the power on the power supply.
        """
        if self._power_supplies:
            for i in range(0, len(self._power_supplies)):
                self._power_supplies[i].set_channel(0)
                self._power_supplies[i].apply_v_and_i(0.0, 1.5)
                self._power_supplies[i].disable()
                time.sleep(100e-3)
                self._power_supplies[i].set_channel(1)
                self._power_supplies[i].apply_v_and_i(0.0, 3.0)
                self._power_supplies[i].disable()
                time.sleep(100e-3)
                self._power_supplies[i].set_channel(2)
                self._power_supplies[i].apply_v_and_i(0.0, 3.0)
                self._power_supplies[i].disable()
                self._power_supplies[i].set_channel(0)
