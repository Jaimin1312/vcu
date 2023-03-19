''' Classes to support interaction with the VCU.
'''
import re
import logging
from fabric import Connection
from vcs.model import application

VISALPHAC_PATH = r'~/abc3dv2/visalphac'
I2C_ID_FOR_DESERIALIZER_1 = 9
I2C_ID_FOR_DESERIALIZER_2 = 10
PASSWORD = application.settings.values.vcu_password

i2cdetect_extractor = re.compile(
    r'^40:\s(--|UU)\s(--|UU)\s(--|UU)\s(--|UU)', re.DOTALL|re.MULTILINE)
hash_extractor = re.compile(r'^([0-9,a-f]{40})\s+([ \S]+)$', re.DOTALL|re.MULTILINE)
boottime_extractor = re.compile(r'^.*= (.*)s$', re.MULTILINE|re.DOTALL)



class VCU:
    """ Manages connections to the Jetson Xavier on the VCU to provide
    ability to capture images and determine device assignment for attached cameras.

    Args:
        address (str, optional): IP address of the target computer on the VCU.
            Defaults to TARGET.
    """
    def __init__(self, deserializer_lookup, address=None):
        self._address = address if address is not None else application.settings.values.vcu_hostname
        self._deserializer_lookup = deserializer_lookup
#        self._log(self._address)
        self._connection = Connection(
            self._address,
            connect_kwargs={"password": application.settings.values.vcu_password},
            connect_timeout=3
        )


    def connect(self):
        """ Connect to the VCU over SSH.
        """
        self._connection.open()


    def disconnect(self):
        """ Disconnect SSH session to VCU.
        """
        self._connection.close()


    def acquire_images(self, destination):
        """ Capture and download a set of images and movies from all 8 cameras.

        Uses SCP to copy images back to host machine.

        Args:
            destination (str): path to the folder where images will be copied
        """
        _capture_camera_output_v3(self._connection)
        _get_contents(self._connection, 'camera-capture/images', destination)


    def generate_camera_position_lookup(self) -> dict:
        """ Generates a lookup table that equates a camera position to a device id

            NOTE: there are two deserializers and postions on each are assigned in order,
                and deserializer1 is assigned after deserializer2.  If there are any gaps,
                the address is assigned to the next in order.

        Args:
            connection (Connection): fabric connection to the VCU host.

        Returns:
            dict: lookup table of camera ID to device.
        """
        lookup = {}
        device_index = 0    # Devices are assigned in order, regardless of position.

        #NOTE: The order is important as the kernel assigns addresses for Deserializer1 first
        for deserializer_id in [I2C_ID_FOR_DESERIALIZER_1, I2C_ID_FOR_DESERIALIZER_2]:
            i2c_slots = poll_i2c_device(self._connection, deserializer_id)
            logging.debug('i2c_slots for device #%s:\t%s', deserializer_id, i2c_slots)
            for index, slot in enumerate(i2c_slots):
                if slot:
                    camera_position = self._deserializer_lookup[deserializer_id][index]
                    lookup.update({device_index:camera_position})
                    device_index += 1

        return lookup


    def software_version_check(self):
        """ Capture the version and hash of key software components on the VCU.
        This is useful for determining whether the VCU has the latest valid software
        configuration.

        Returns:
            tuple(dict(str, str), str): Tuple containing a dictionary of hashes and the
                server version.
        """
        targets = [
            '/usr/bin/symbot_server-0.4',
            '/usr/bin/symbot_client-0.4',
        ]

        hashes = _get_hashes(self._connection, targets)
        version = _get_symbot_client_version(self._connection)

        return hashes, version


    def get_thermal_data(self):
        """ Records the thermal readings from various parts of the Xavier SOM.

        Returns:
            dict: Collection of named temperature recordings.
        """
        temperatures = _get_temperatures(self._connection)
        return temperatures


    def get_boot_time(self) -> float:
        """ Returns the boot time calculated by systemd-analyze.

        Returns:
            float: boot time in seconds.
        """
        response = self._connection.run('systemd-analyze')
        logging.debug(response)
        matches = boottime_extractor.match(response.stdout)
        boot_time = float(matches.group(1))

        return boot_time



def _get_hashes(connection: Connection, targets: list[str]):
    hash_lookup = {}
    for target in targets:
        response = connection.run(f'sha1sum {target}')
        logging.debug(response)
        matches = hash_extractor.search(response.stdout)
        assert matches is not None, f"Unable to parse sha1sum output to determine hash of {target}"
        filehash, filename = matches.groups()
        logging.debug('%s has the following hash: %s', filename, filehash)
        hash_lookup[target] = filehash

    return hash_lookup


def _get_temperatures(connection: Connection):
    types = connection.run('cat /sys/class/thermal/thermal_zone*/type').stdout.splitlines()
    temps = connection.run('cat /sys/class/thermal/thermal_zone*/temp').stdout.splitlines()
    assert len(types) == len(temps), "mismatch in length between temps and types"
    numeric_temps = [float(temp)/1000 for temp in temps]

    temperatures = dict(zip(types, numeric_temps))
    logging.debug("Temperature Details:  %s", temperatures)

    return temperatures


def _get_symbot_client_version(connection: Connection):
    response = connection.run('symbot_client-0.4 --version')
    version = response.stdout.strip()
    logging.debug("Symbot Version (self-reported): %s", version)

    return version



def poll_i2c_device(connection: Connection, device_id: int) -> list:
    """ Returns list of positions used by detected i2c chips

    NOTE: This helps determine whether or not a camera is connected.
        We expect addresses 0x40-0x43 to be used for each deserializer when all cameras
        are connected.  As address is assumed to be "used" when i2cdetect returns a "UU"
        for this spot, indicating that the kernel has reserved this address for
        a connected camera.
        We expect i2c cameras for device 9 and 10.

    Args:
        connection (Connection): [description]
        device_id (int): [description]

    Returns:
        list: [description]
    """
    response = connection.run(f'echo {PASSWORD} | sudo -S i2cdetect -y -r {device_id}')
    logging.debug('poll_i2c_device for device #%s\n%s', device_id, response)
    matches = i2cdetect_extractor.search(response.stdout)
    assert matches is not None, "Unable to parse i2cdetect output to determine device list"

    return [part == 'UU' for part in matches.groups()]


def _capture_camera_output_v3(connection):
    output = connection.run('rm -rf camera-capture')
    logging.debug(output)
    output = connection.run('mkdir -p camera-capture')
    logging.debug(output)

    connection.put('./assets/capture.sh', 'camera-capture/capture.sh')
    connection.put('./assets/camconfig-8a.json', 'camera-capture/camconfig-8a.json')
    connection.put('./assets/camconfig-8b.json', 'camera-capture/camconfig-8b.json')
    output = connection.run('chmod +x camera-capture/capture.sh', echo=True)
    logging.debug(output)
    output = connection.run('bash ~/camera-capture/capture.sh', echo=True)
    logging.debug(output)

    # Restart the argus daemon to avoid issues with repeatablility
    # See https://forums.developer.nvidia.com/t/libargus-fails-on-re-entry-if-killed/82388
    output = connection.run(f'echo {PASSWORD} | sudo -S systemctl restart nvargus-daemon')
    logging.debug(output)


def _list_contents(connection, target):
    parts = [part for part in connection.run(f'ls {target}').stdout.split('\n') if part]
    logging.debug("List contents of %s: %s", target, parts)
    return parts


def _get_contents(connection, src, dst):
    parts = _list_contents(connection, src)
    for part in parts:
        print('.', end='')
        connection.get(f'{src}/{part}', f'{dst}/{part}')
