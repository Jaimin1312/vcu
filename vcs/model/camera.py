''' Module with support for Camera definition.
'''
import os
import re
from typing import List, Optional

# Used to extract the position information from the image filename.
index_extractor = re.compile(r'.*device(\d).*', re.DOTALL)


class Camera:
    """ Camera representation that associates images with camera index and serial number.
    Args:
        index (int): index of the camera.
        serial_number (str): serial number of the camera assembly.
    """
    def __init__(self, index: int, serial_number: str):
        self.index: int = index
        self.serial_number: str = serial_number
        self._image_paths: List[str] = []
        self._status = None
        self._report = {}


    def associate_image_path(self, image: str):
        """ Associate an image path with the camera.

        Args:
            image (str): path to the image to associate.
        """
        self._image_paths.append(image)


    @property
    def first_image_path(self) -> Optional[str]:
        """ Path to the first image.

        Returns None if there are no associated images.
        """
        image_list = [path for path in self._image_paths if path.endswith('.png')]
        return image_list[0] if image_list else None


    @property
    def images(self):
        """ List of associated image paths.
        """
        return self._image_paths


    @property
    def has_expected_images(self) -> bool:
        """ Indicates whether the camera has the expected images.

        If no serial number is provided, one would expect no associated images.
        If a serial number is provided, one would expect one or more images.
        If neither of these constraints are met, return false to indicate an unexpected condition.
        """
        return (self.serial_number == "" and len(self.images) == 0) or \
            (self.serial_number != "" and len(self.images) > 0)


    def set_status(self, status):
        """ Set the pass/fail status of the camera.
        """
        self._status = status


    def set_report(self, report):
        """ Set the image report for the camera.
        """
        self._report = report


    def get_status_message(self):
        """ Returns a status message for the given camera.

        Returns:
            str: description of the camera status with pass/fail status and key results.
        """
        return ("    Camera {id}:\t{passfail} --> {summary}".format(
            id=self.index + 1,
            passfail=('pass' if self._status else 'fail' if self._status is not None else 'n/a'),
            summary=', '.join([f'{key}={value:.2f}' for image in self._report.values() for
                               key, value in image.items()]),
        ))



def assign_images_to_cameras(camera_list: list[Camera], path_to_image_folder: str,
                             camera_position_lookup: dict):
    """ Assigns all image paths in the provided directory and assigns them to the related Camera
    object as determined by the camera lookup table.

    This uses a provided lookup table to associate the index extracted from the image name to an
    actual camera position.  This is important to provide as the index can change relative meaning
    on a system where not all of the cameras have been provided.

    Args:
        camera_list (list[Camera]): list of Camera objects with which to associate images.
        path_to_image_folder (str): path to directory containing images.
        camera_position_lookup (dict): lookup table of listed camera index to actual position.
    """
    for path in os.listdir(path_to_image_folder):
        if path.endswith('.png'):
            match = index_extractor.match(path)
            assert match is not None, f'Unable to extract index from path "{path}"'
            camera_index = int(match.group(1))
            if camera_index in camera_position_lookup:
                actual_camera_index = camera_position_lookup[camera_index]
                camera = camera_list[actual_camera_index]
                full_path = os.path.join(path_to_image_folder, path)
                camera.associate_image_path(full_path)
