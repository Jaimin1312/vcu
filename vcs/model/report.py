''' Reporting related classes used by utility.

CameraAssessmentReport: used to store summary and details on the image quality assessment.
'''
import json
from vcs.model import log


def write(path: str, content):
    """ Write the assessment report to disk.

    Args:
        path (str): path to where the report should be written.
    """
    log.makedirs(log.dirname(path))
    with open(path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(content, indent=4))


class CameraAssessmentReport:
    """ Writes a report of the image quality assessment details for a camera to disk.

    Args:
        camera_id (object): camera identity.
        camera_status (boolean): pass/fail summary of the image quality assessment.
        iqa_report (dict): image quality assessment details.
    """
    def __init__(self, camera_id, camera_status, iqa_report: dict):
        self._camera_id = camera_id
        self._camera_status = camera_status
        self._iqa_report = iqa_report


    def write(self, path: str):
        """ Write the assessment report to disk.

        Args:
            path (str): path to where the report should be written.
        """
        write(path, self._content)


    def read(self, path: str):
        """ Reads the assesment report from disk.

        Args:
            path (str): path to the report to load.
        """
        raise NotImplementedError("CameraAssessmentReport.read not currently supported!")


    @property
    def _content(self):
        content = {
            'camera_id':self._camera_id,
            'camera_status':self._camera_status,
            'image_quality_assessment':self._iqa_report,
        }
        return content
