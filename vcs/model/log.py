""" Logging support.

Provides a list of functions to assist with tailoring the logging module
to this given application.
"""

import os
import re
import datetime
import logging
import unicodedata
from os.path import dirname, join

from . import application


def close(logger):
    "Reset the logger by removing all event handlers."
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])



def initialize(filename, console_stream=None, transaction_filename=None):
    """Set the default logger.

    Write to the given file as well as the console_stream."""
    makedirs(dirname(filename))
    logger = logging.getLogger()
    close(logger)

    # Setup logging for primary file
    logging.basicConfig(filename=filename, level=logging.DEBUG,
                        format='%(asctime)-15s;%(levelname)8s;%(message)s')
    if console_stream:
        stream_handler = logging.StreamHandler(console_stream)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(stream_handler)

    # Setup transaction file logging where required
    if transaction_filename:
        makedirs(dirname(transaction_filename))
        transaction_handler = logging.FileHandler(transaction_filename)
        transaction_handler.setLevel(logging.INFO)
        transaction_handler.setFormatter(
            logging.Formatter('%(asctime)-15s;%(levelname)8s;%(message)s'))
        logger.addHandler(transaction_handler)


def makedirs(directory):
    """Create a directory, if it does not already exist.

    An exception is raised if the path exists, but is not a directory.
    """
    if not os.path.isdir(directory):
        os.makedirs(directory)


def get_timestamp() -> str:
    """ Returns the latest timestamp string.

    Returns:
        str: representation of timestamp in ISO8601-1:2019 basic format YYmmddTHHMMSS.
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    return timestamp


def batch_dir(directory, timestamp):
    """ Builds a string of the path to a timestamped batch directory.

    Args:
        directory (str): Parent directory
        timestamp (str): Timestamp in ISO8601-1:2019 basic format YYmmddTHHMMSS.

    Returns:
        str: batch directory path
    """
    return join(directory, f"VCU_Test_BatchLogs_{timestamp}")


def get_diagnostic_log_path(directory: str) -> str:
    """ Builds the path to the diagnostic log.

    Args:
        directory (str): parent directory
        timestamp (str): timestamp to use for the current batch

    Returns:
        str: path to the diagnostic log
    """
    return join(directory, "diagnostic.log")


def get_transaction_log_path(part_number, serial_number, directory):
    """ Build path for the current transaction log.

    NOTE: transaction logs are kept in a subfolder under the parent logging directory.

    Args:
        part_number (str): part number of camera used in log name.
        serial_number (str): serial number of camera used in log name.
        directory (str): parent logging directory

    Returns:
        str: path to the current transaction log file.
    """
    timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    transactions_directory = get_transactions_directory_path(directory)
    serial_number = slugify(serial_number)
    return join(transactions_directory, f'VCU_Test_{part_number}_{serial_number}_{timestamp}.log')


def get_transactions_directory_path(directory: str) -> str:
    """ Build path to transaction log directory.

    Args:
        directory (str): parent logging directory.

    Returns:
        str: path to tranactions loggging subdirectory.
    """
    return join(directory, 'transactions')


def open_log(log_directory):
    "Open a log file named with the module's serial number."

    primary_log_path = get_diagnostic_log_path(log_directory)
    initialize(primary_log_path)
    logging.info('----------')
    logging.info('PRODUCT:%s %s', application.COMPANY, application.PRODUCT)
    logging.info('VERSION:%s', application.VERSION)
    logging.info('PART:%s', application.ITEM_NUM_VPCB)


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
