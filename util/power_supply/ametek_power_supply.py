"""Control an Ametek power supply."""

# Copyright Symbotic 2015

import io
import logging
import time
import serial
import serial.tools.list_ports

from .errors import NotDetected, MultipleSupplies

class Power:
    def __init__(self, port_name):
        self._serial = serial.Serial(port=port_name, baudrate=9600, timeout=0.1)
        self._stream = io.TextIOWrapper(self._serial)
        self.command_period = 0.1
        self.last_command_time = time.time() - self.command_period
        self.status_clear()
        self.select_address(1)
        self.port_name = port_name
        self.identity = self.identify()
        if not self.identity or not self.identity.startswith("AMETEK"):
            raise NotDetected(port_name)
        logging.info('POWER:OPEN %s %s', port_name, self.identity)

    def name(self):
        return self._serial.name

    def flush(self):
        self._stream.flush()

    def duration_until_ready_for_next_command(self):
        return max(0, self.command_period + self.last_command_time - time.time())

    def wait_until_ready_for_next_command(self):
        while self.duration_until_ready_for_next_command() > 0:
            time.sleep(self.duration_until_ready_for_next_command())

    def write(self, string):
        self.wait_until_ready_for_next_command()
        self._stream.write(string+"\n")
        self.flush()
        self.last_command_time = time.time()

    def read(self):
        self.wait_until_ready_for_next_command()
        return self._stream.readline().strip()

    def retry(self, function):
        try:
            return function()
        except Exception:
            logging.info('POWER:RETRY')
            return function()

    def query_selected_address(self):
        self.write("*ADR?")
        return int(self.read())

    def selected_address(self):
        return self.retry(self.query_selected_address)

    def select_address(self, index):
        self.retry(lambda: self._select_address(index))

    def _select_address(self, index):
        self.write("*ADR "+str(index))
        self.check()

    def voltage(self):
        self.write(":VOLT?")
        return float(self.read())

    def set_voltage(self, voltage):
        self.retry(lambda: self._set_voltage(voltage))
        logging.info('POWER:SET {}V'.format(voltage))

    def _set_voltage(self, voltage):
        self.write(":VOLT " + str(voltage) + "V")
        self.check()
        if voltage != self.voltage():
            raise Exception("Error setting the power supply voltage.")

    def current_limit(self):
        self.write(":CURR?")
        return float(self.read())

    def set_current_limit(self, amps):
        self.retry(lambda: self._set_current_limit(amps))
        logging.info('POWER:SET %dA', amps)

    def _set_current_limit(self, amps):
        self.write(":CURR " + str(amps) + "A")
        self.check()
        if self.current_limit() != amps:
            raise Exception("Error setting the power supply current.")

    def measured_current(self):
        """Return the current usage in amps"""
        self.write(":MEAS:SCAL:CURR?")
        return float(self.read())

    def enabled(self):
        return self.retry(self._enabled)

    def _enabled(self):
        self.write("OUTP?")
        return int(self.read())

    def enable(self):
        self.retry(self._enable)
        logging.info('POWER:ENABLE')

    def _enable(self):
        self.write("OUTP ON")
        self.check()
        if self.enabled() != 1:
            raise Exception("Could not enable the power supply.")

    def disable(self):
        self.write("OUTP OFF")
        self.check()
        e = self.enabled()
        if e != 0:
            raise Exception("Could not disable the power supply: "+str(e))
        logging.info('POWER:DISABLE')

    def identify(self):
        self.write("*IDN?")
        result = self.read()
        self.check()
        return result

    def error(self):
        self.write("*ERR?")
        return self.read()

    def check(self):
        error = self.error()
        if error and error != '0,"No error;"':
            raise Exception(error)

    def status_clear(self):
        self.retry(self._status_clear)

    def _status_clear(self):
        self.write("*CLS")
        self.check()

    def status_byte(self):
        self.write(":STAT1:SBYTE?")
        return self.read()

    def wait_message_available(self):
        ready = False
        while not ready:
            try:
                status = int(self.status_byte())
                if status & 4:
                    self.check()
                ready = status & 16
            except Exception:
                pass

    def standard_event_status(self):
        self.write(":STAT1:STAN?")
        return int(self.read())

    def operation_complete(self):
        self.write("*OPC?")
        return int(self.read())

    def wait_operation_complete(self):
        ready = False
        while not ready:
            ready = self.operation_complete() & 1

    def close(self):
        self._stream.close()
        self._serial.close()



def _probe():
    """Probe for power supplies.

    The probe() generator enumerates all attached AMETEK power supplies.
    """
    for (port_name, _, _) in com_ports():
        try:
            yield Power(port_name)
        except NotDetected:
            pass
        except Exception as err:
            pass


def open():
    """ Returns an instance of a Ametek power supply.  Returns None of nothing is found.

    Raises:
        power_supply.MultipleSupplies: raised if multiple power supplies are detected.

    Returns:
        Power: instance of Ametek power supply.
    """
    power_supplies = list(_probe())
    if power_supplies:
        if len(power_supplies) > 1:
            raise MultipleSupplies()
        found_power_supply = power_supplies[0]
        print("opened power supply " + found_power_supply.name())
        return found_power_supply
    else:
        return None


def com_ports():
    ''' Provides a list of serial/com ports associated with the FTDI manufacturer.
    '''
    def _port(port):
        ''' Checks that a provided port is associated with the FTDI manufacturer.
        '''
        return port.manufacturer.startswith('FTDI')

    return filter(_port, serial.tools.list_ports.comports())
