"Control a BK Precision (e.g., 1685B, 1687B, 1688B, or 9140-GPIB) power supply."

# Copyright Symbotic 2023

import logging
import pyvisa

from .errors import NotDetected, MultipleSupplies


ENABLE_COMMAND = { True: "OUTP ON", False: "OUTP OFF" }

class OperationFailed(Exception):
    pass


class Power:
    """Model of a BK Precision 9140-GPIB power supply.

    The 9140 series are both USBTMC and USB VCP compliant.

    The VISA Resource string gives USB0::<Vendor ID>::<Product ID>::<Serial Number>:INSTR
        Example From figure 7.1 :
        <Vendor ID> = 0x3121
        <Product ID> = 0x0001 for 9140 or 0x0002 for 9141
        <Serial Number> = 583k20101

    When using USBVCP set the port setting to:

        Port Settings
        Baud Rate       9600
        Data bits       8
        Parity          None
        Stop bits       1
        Flow control    None

    For comparision, the following info is from the 168xB_programming_manual.pdf:
        3 Command Set
        Note: In order to use remote commands, please make sure to use the following communication settings - Baud rate: 9600, Data bits: 8, Parity: none, Stop bits: 1. If you are using HyperTerminal, make sure to check your ASCII setup to not append line feeds.
        Command line format: COMMAND<parameter1><parameter2>…[CR]
        Current value will have one decimal place for models 1687B and 1688B, and two decimal places for Model 1685B.
    """

    def __init__(self):
        """Open a BK Precision 9140-GPIB power supply."""
        self._rm = pyvisa.ResourceManager()
        self._li = self._rm.list_resources()
        for index in range(len(self._li)):
            print(str(index)+" - "+self._li[index])
        self._vi = self._rm.open_resource(self._li[0])
        self.identity = self.identify()
        self.selected_channel = self.set_channel(0)
        self.applied_v_and_i = self.apply_v_and_i(0.000, 2.000)
        logging.info('POWER:*IDN {}'.format(self.identity))

    def apply_v_and_i(self, voltage, current):
        """Description  Set and query the voltage and current of the selected channel.

        Command Syntax  APPLy <voltage>,<current>

        Query Syntax    APPLy?

        Example         APPL 10,1

        Query Respond   APPL?

        Returns:        10,1
        """
        self._vi.write(f"APPL {voltage},{current}")
        response = self._vi.query("APPL?").rstrip('\n')
        formatted = str(format(voltage, '.3f')) + ',' + str(format(current, '.3f'))
        if response == formatted:
            print(f"Power Supply Apply Voltage and Current Response: %s" % (response,))
            logging.info(f"POWER:APPL {voltage}V, {current}A")
            return response
        else:
            raise OperationFailed('Could not read the voltage and current from the Precision 9140-GPIB power supply.')

    def identify(self):
        """Description The *IDN? query causes the instrument to identify itself. The response comprises manufacturer, model,
        serial number, software version and firmware version.

        Query       *IDN?

        Response    *IDN, <device id>,<model>,<serial number>, <software version>,
                    <hardware version>.
                    <device id>:=“B&K” is used to identify instrument.
                    <model>:= A model identifier less than 14 characters will contain the model number.
                    <serial number>:= Number that uniquley identifies the instrument.
                    <firmware version>:= Firmware revision number.
                    <hardware version>:= Hardware revision number.
        
        Example     *IDN?
                    Returns: B&KPrecision,9140,*********,1.06-1.04
        """
        response = self._vi.query("*IDN?").rstrip('\n')
        if response is not None:
            print(f"Power Supply Identify Response: ", response)
            return response
        else:
            raise OperationFailed('Could not read instrument identification from the Precision 9140-GPIB power supply.')

    def set_channel(self, channel):
        """Select a channel. When a channel is selected all other channels are unavailable for
        programming until selected. By default channel one is selected.
        0 = Channel 1
        1 = Channel 2
        2 = Channel 3
        """
        self._vi.write(f"INST {channel}")
        response = self._vi.query("INST?").rstrip('\n')
        formatted = 'CH' + str(channel + 1)
        if response == formatted:
            print("Power Supply Set Channel Response: ", response)
            logging.info(f"POWER:INST {channel}")
            self.selected_channel = response
            return response
        else:
            raise OperationFailed('Could not read the channel from the Precision 9140-GPIB power supply.')

    def set_enable(self, value):
        """Enable/disable the output."""
        self._vi.write(ENABLE_COMMAND[value])
        response = bool(int(self._vi.query("OUTP?").rstrip('\n')))
        if response == value:
            print("Power Supply Enable Response: ", response)
            return response
        else:
            raise OperationFailed('Could not read the enabled status from the Precision 9140-GPIB power supply.')

    def measure_all(self):
        """Query the voltage, current, and power of the selected channel."""
        response = self._vi.query("MEAS:ALL?").rstrip('\n')
        if response is not None:
            print(f"Power Supply Measure All Response: %s" % (response,))
            logging.info(f"POWER:MEAS:ALL {response}")
            return response
        else:
            raise OperationFailed('Could not read voltage, current, and power from the Precision 9140-GPIB power supply.')

    def measure_all_channels(self):
        """Query the voltage, current, and power of all channels based on operation mode.
            1. Operation mode is normal [CH1, CH2, CH3].
                • Return: CH1 V, A, W, CH2 V, A, W, CH3 V,A ,W [9 data values]
            2. Operation mode is CH1 + CH2 series [CH1 + CH2 (series), CH3].
                • Return: CH1 + CH2 V, A, W, CH3 V, A, W [6 data values]
            3. Operation mode is All CH in series [CH1 + CH2 + CH3 (series)].
                • Return: CH1 + CH2 + CH3 V, A, W [3 data values]
        """
        response = self._vi.query("MEAS:ALLCH?").rstrip('\n')
        if response is not None:
            print(f"Power Supply Measure All Response: %s" % (response,))
            logging.info(f"POWER:MEAS:ALLCH {response}")
            return response
        else:
            raise OperationFailed('Could not read voltage, current, and power of all channels from the Precision 9140-GPIB power supply.')

    def measure_current(self):
        """Description  Query the current voltage.

        Query           :MEASure[:SCALar]:CURRent[:DC]?

        Response        <NRf>
        """
        response = self._vi.query("MEAS:CURR?").rstrip('\n')
        if response is not None:
            print(f"Power Supply Measure Current Response: ", response)
            logging.info(f"POWER:MEAS:CURR {response}")
            return response
        else:
            raise OperationFailed('Could not read current from the Precision 9140-GPIB power supply.')

    def measure_power(self):
        """Description  Query measured power.

        Query           :MEASure[:SCALar]:POWer[:DC]?

        Example         MEAS:POW?

        Response        <NRf>
        """
        response = self._vi.query("MEAS:POW?").rstrip('\n')
        if response is not None:
            print(f"Power Supply Measure Power Response: ", response)
            logging.info(f"POWER:MEAS:POW {response}")
            return response
        else:
            raise OperationFailed('Could not read power from the Precision 9140-GPIB power supply.')

    def measure_voltage(self):
        """Description  Query the measured voltage.

        Query           :MEASure[:SCALar]:VOLTage[:DC]?

        Response        <NRf>
        """
        response = self._vi.query("MEAS:VOLT?").rstrip('\n')
        if response is not None:
            print(f"Power Supply Measure Voltage Response: ", response)
            logging.info(f"POWER:MEAS:VOLT {response}")
            return response
        else:
            raise OperationFailed('Could not read voltage from the Precision 9140-GPIB power supply.')

    def enable(self):
        """Enable the output of the selected channel."""
        self.set_enable(True)
        logging.info('POWER:OUTP:STAT ON')

    def disable(self):
        """ Disable the output of the selected channel."""
        self.set_enable(False)
        logging.info('POWER:OUTP:STAT OFF')


def probe():
    """Probe for power supplies.

    The probe() generator enumerates all attached B & K power supplies.
    """
    try:
        yield Power()
    except NotDetected:
        pass


def open():
    supply_gen = probe()
    try:
        supplies = []
#        supply = supplies.__next__()
        supplies.append(next(supply_gen))
#        supplies.append(next(supply_gen))
#        supplies.append(next(supply_gen))
        try:
            supply_gen.__next__()
            raise MultipleSupplies()
        except StopIteration:
            return supplies
    except OperationFailed:
        return None
    except StopIteration:
        return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='BK Precision 9140-GPIB Power Supply Control')
    parser.add_argument('--enable', dest='enable', action='store_const', const=True, help='Enable the power supply output.')
    parser.add_argument('--disable', dest='enable', action='store_const', const=False, help='Disable the power supply output.')
    parser.add_argument('--voltage', type=float, help='Set the power supply voltage.')
    parser.add_argument('--current', type=float, help='Set the power supply current limit.')
    args = parser.parse_args()
    supply = open()
    if supply is None:
        print('No BK Precision 9140-GPIB Power Supply was detected.')
        exit(1)
    if args.enable is not None:
        supply.set_enabled(args.enable)
    if args.voltage is not None:
        supply.set_voltage(args.voltage)
    if args.current is not None:
        supply.set_current_limit(args.current)
    print(supply.name())
    print('Limits: %2.1f V  %1.2fA' % (supply.voltage(), supply.current_limit()))
    print('Actual: %2.2fV  %1.2fA' % (supply.measured_voltage(), supply.measured_current()))
    supply.close()
