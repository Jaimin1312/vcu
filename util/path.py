"""Path manipulation functions.
"""

# Copyright Symbotic 2013

import os
import sys
import __main__

def makedirs(directory):
    """Create a directory, if it does not already exist.

    An exception is raised if the path exists, but is not a directory.
    """
    if not os.path.isdir(directory):
        os.makedirs(directory)


def split(full_path):
    """Split a path into directory, base-name and extension.

    >>> split('root/src/main.py')
    ('root/src', 'main', '.py')
    """
    path, full_path = os.path.split(full_path)
    name, ext = os.path.splitext(full_path)
    return path, name, ext


def executable_path() -> str:
    """ Returns path to current executable.

    Correctly adjusts when the executable is frozen due to cx_Freeze.

    Returns:
        str: path to the current executable
    """
    if getattr(sys, 'frozen', False):
        executable = sys.executable
    else:
        executable = os.path.abspath(f"{__file__}/..")
    return executable


def data_dir() -> str:
    """ Returns the directory containing the current executable.

    Suitable for use as a data directory or when loading in related file assets.
    Correctly adjusts for when the exectuable is frozen due to cx_Freeze.

    Returns:
        str: path to the directory containing the current executable.
    """
    return os.path.dirname(executable_path())


def get_path_relative_to_application(path: str) -> str:
    """ Builds a path relative to the current application.

    Suitable for use as a data directory or when loading in related file assets.
    Correctly adjusts for when the exectuable is frozen due to cx_Freeze.

    Args:
        path (str): Partial path relative to the current executable

    Returns:
        str: Absolute path relativ eto the current executable
    """
    return os.path.abspath(
        os.path.join(data_dir(), path)
        )
