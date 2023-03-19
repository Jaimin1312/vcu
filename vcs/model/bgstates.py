''' Module provides class to store valid states for use with background worker.
'''
from util.fsm import State


class BGStates:                                             #pylint: disable=too-few-public-methods
    """ Available states used by the camera test state machine.
    """
    IDLE = State("")
    WAITING = State("Waiting for response...")
    SETUP = State("Setting up equipment")
    CONNECTING = State("Connecting")
    VERSION_CHECK = State("Checking VCU software configuration")
    CAMERA_CHECK = State("Checking for camera presence")
    THERMAL_CHECK = State("Checking system temperatures")
    ACQUIRE_IMAGES = State("Acquiring images")
    PROCESS_IMAGES = State("Processing images")
    REVIEW = State("Reviewing results")
    ABORT = State("Aborting")
    CLEANUP = State("Cleaning up")
