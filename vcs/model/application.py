""" Application constants for Vision System Utilities.
"""
from os.path import join
import dataclasses
import appdirs

from util.settings import ApplicationSettings, set_default, get_install_timestamp

COMPANY = 'Symbotic'
PRODUCT = 'VCS Utilities'
VERSION = '1.0.3'

# Arena Item Name, Item Number, & Revision
ITEM_NAME_ECU = 'ASSEMBLY, ECU'                 # Item Name for ECU, Vision
ITEM_NAME_VCAMENC = 'ASSY, CAMERA ENCLOSURE'    # Item Name for Camera Enclosure, Vision
ITEM_NAME_VPCB = 'PCB Vision Mezzanine, Symbot' # Item Name for PCBA, Vision
ITEM_NUM_ECU = '410-02774'                      # Item Number for ECU, Vision
ITEM_NUM_VCAMENC = '410-02642'                  # Item Number for Camera Enclousre, Vision
ITEM_NUM_VPCB = '372-00154'                     # Item Number for PCBA, Vision
REVISION_ECU = 'A'                              # Revision for ECU, Vision
REVISION_VCAMENC = 'A'                          # Revision for Camera Enclosure, Vision
REVISION_VPCB = '3'                             # Revision for PCBA, Vision

# Combine Arena Item Number, Revision, & Name
NRN_ECU = f"{ITEM_NUM_ECU} rev {REVISION_ECU} {ITEM_NAME_ECU}"
NRN_VCAMENC = f"{ITEM_NUM_VCAMENC} rev {REVISION_VCAMENC} {ITEM_NAME_VCAMENC}"
NRN_VPCB = f"{ITEM_NUM_VPCB} rev {REVISION_VPCB} {ITEM_NAME_VPCB}"

# Directory for application data
APPLICATION_DATA_PATH = appdirs.site_data_dir(PRODUCT, COMPANY)
APPLICATION_SETTINGS_PATH = join(APPLICATION_DATA_PATH, 'settings.yaml')

class MapperForCameraTest():
    """ Maps unique element of the Camera Test for use in the View and Controller.
    """
    device_count = 8
    device_term = "Camera"
    enable_transaction_log = True
    get_deserializer_lookup = lambda: settings.values.deserializer_lookup_camera
    @classmethod
    def get_serial_numbers(cls, device_list_values):
        """ Maps the list of serial numbers to use for the camera devices.
        """
        return device_list_values

    def __str__(self):
        return "Mapper for Camera Test"


class MapperForVCUTest():
    """ Maps unique element of the VCU Test for use in the View and Controller.
    """
    device_count = 1
    device_term = "VCU"
    enable_transaction_log = False
    get_deserializer_lookup = lambda: settings.values.deserializer_lookup
    @classmethod
    def get_serial_numbers(cls, _):
        """ Maps the list of serial numbers to use for the camera devices.
        Using default values in the VCU test as the cameras are not the UUT
        in this scenario.
        """
        return [
            'camera_sn_01',
            'camera_sn_02',
            'camera_sn_03',
            'camera_sn_04',
            'camera_sn_05',
            'camera_sn_06',
            'camera_sn_07',
            'camera_sn_08',
        ]

    def __str__(self):
        return "Mapper for VCU Test"


@dataclasses.dataclass
class _DefaultSettings:
    """ Define the default values used for settings.
    These values will be used for any missing settings keys or incase the external settings
    file fails to load.
    """
    installation_timestamp: str = set_default(get_install_timestamp())
    logging_path: str = join(APPLICATION_DATA_PATH, "logs")
    vcu_hostname: str = r'botuser@vis08170'
    vcu_password: str = 'root'
    deserializer_lookup: dict = set_default(
        {
            9:{
                0:0,
                1:3,
                2:5,
                3:6,
            },
            10:{
                0:7,
                1:4,
                2:1,
                3:2,
            },
        })
    deserializer_lookup_camera: dict = set_default(
        {
            9:{
                0:3,
                1:4,
                2:5,
                3:6,
            },
            10:{
                0:7,
                1:0,
                2:1,
                3:2,
            },
        })


def get_application_settings():
    """ Create an instance of ApplicationSettings class used to load/save/reset settings from file.
    """
    temp = ApplicationSettings(
        path=APPLICATION_SETTINGS_PATH,
        defaults=_DefaultSettings(),
    )
    temp.load()
    temp.save()

    return temp


# Instance of application settings accessible from the module
settings = get_application_settings()
