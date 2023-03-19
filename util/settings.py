""" Used to manage a settings files with options for loading, saving, and resetting to defaults.

Settings files are written in YAML format.
A dataclass instance is to be provided as a means for defining the structure and default values.
"""

import os
import dataclasses
from os.path import getmtime
from datetime import datetime
import yaml


class ApplicationSettings:
    """ Used to manage a settings files with options for loading, saving, and resetting to defaults.

    Args:
        path (str): path to a settings file.
        defaults (Any): a class that defines a set of defaults.
            This is expected to be an instance of a dataclass.
    """
    def __init__(self, path, defaults):
        self.path = path
        self._defaults = dataclasses.replace(defaults)
        self._current_values = dataclasses.replace(defaults)


    def save(self):
        """ Write the current setting values to a settings file.
        """
        serialized_data = yaml.dump(
            self._current_values.__dict__, Dumper=_CustomYamlDumper, default_flow_style=False)

        # Create parent directory if not present
        parent = os.path.dirname(self.path)
        if not os.path.exists(parent):
            os.makedirs(parent)

        with open(self.path, 'w', encoding='utf-8') as ref:
            ref.write(serialized_data)


    def load(self):
        """ Replace the current settings values with those stored in the settings file.

        Use the default value if the stored settings file is missing a setting.
        """
        if not os.path.exists(self.path):
            self.reset()
            return

        with open(self.path, 'r', encoding='utf-8') as ref:
            try:
                deserialized_data = yaml.safe_load(ref.read()) or {}
            except yaml.scanner.ScannerError:
                deserialized_data = {}
            self.reset()
            self._current_values = dataclasses.replace(self._defaults)
            for name, value in deserialized_data.items():
                if name in self._current_values.__dict__.keys():
                    setattr(self._current_values, name, value)


    def reset(self):
        """ Restore current settings values to their defaults.
        """
        self._current_values = dataclasses.replace(self._defaults)


    @property
    def values(self):
        """ Provides access to list of current settings values.
        """
        return self._current_values


# Example of method for getting default settings
def _get_default_settings():
    # Define the default values used for settings.
    # These values will be used for any missing settings keys or incase the external settings
    # file fails to load.
    class _ExampleObject(dict):
        pass

    @dataclasses.dataclass
    class DefaultSettings:                                                  #pylint: disable=too-many-instance-attributes,missing-class-docstring
        default_partnumber: str = 'DEFAULT_PARTNUMBER'
        installation_timestamp: str = set_default(_ExampleObject())
        lookup_firmware_by_partnumber: dict = set_default({
            '410-00260':r'firmware\LineSensor-version-2-0-gf91a830.hex',
            '410-02562':r'firmware\LineSensor-version-2-1-f3501fda.hex',
            })
        timelog_enabled: bool = False
        transaction_log_export_limit: int = 10

    return DefaultSettings()


def set_default(default):
    """ Used to set a default value in a dataclass.
    Acts as a semantic abstraction to make defining dataclasses easier to read.
    NOTE: This is required when the dataclass member is a complex object.
    """
    return dataclasses.field(default_factory=lambda: default)


def get_install_timestamp():
    mtime = getmtime(__file__)
    time_format = '%Y-%m-%d_%H:%M:%S'
    timestring = datetime.fromtimestamp(mtime).strftime(time_format)
    return timestring


class _CustomYamlDumper(yaml.Dumper):                    #pylint: disable=too-many-ancestors
    """ Customized Yaml Dumper provided to make lists indented and a little nicer to read.
    """
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
