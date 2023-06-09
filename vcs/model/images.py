
''' Module to support various image assessments.

Uses torch package to load images into Tensors and evaluate using a variety of trained models
to generate qualitative numbers.
'''
import logging
import os
from typing import Optional
import cv2
import piq
import torch
from skimage.io import imread
from util.path import get_path_relative_to_application
from vcs.model.camera import Camera, index_extractor


PATH_TO_BASELINES = get_path_relative_to_application(r'assets/baseline-images')
IMAGE_PATH_REFERENCE = get_path_relative_to_application(r'assets/referenceA.jpg')


class Baselines(dict):
    """ loads baseline images into memory and stores them by ID.
    """
    def __init__(self, target):
        super().__init__()
        for filename in os.listdir(target):
            path = os.path.join(target, filename)
            identity = get_image_index(filename)
            image_ref = load_image(path)
            assert image_ref is not None, f"Unable to load {path} as a baseline!"
            self.update({identity:image_ref})


class Image():
    """ loads image data for image processing.
    Keeps both as skimage and tensor formats.

    Removes alpha channel for use with Tensor.
    """
    @torch.no_grad()
    def __init__(self, target_path):
        """ Initialize the image for processing

        Args:
            target_path (str): path to image
        """
        self.image = imread(target_path)
        self.tensor = torch.Tensor(self.image[:,:,:3]).permute(2,0,1)[None, ...] / 255.
        if torch.cuda.is_available():
            self.tensor = self.tensor.cuda()


def evaluate_camera_images(camera: Camera, baselines: Baselines) -> tuple[Optional[bool], dict]:
    """ Load in images associated with a Camera object and evaluate them against
    baseline images to get a set of scores.

    Args:
        camera (Camera): object used to provide access to images taken by a given camera.

    Returns:
        tuple[Optional[bool], dict]: Returns the evaluation status and a set of scores.
    """
    status_list = []
    report = {}

    for path in camera.images:
        image = load_image(path)
        if image is not None:
            baseline_image = baselines[get_image_index(path)]

            scores = analyze_image(image, baseline_image)
            assessment_status = assess_scores(scores)

            status_list.append(assessment_status)
            report.update({path:scores})
        else:
            status_list.append(False)

    status_list.append(camera.has_expected_images)
    status = all(status_list) if len(status_list) > 0 else None

    # Register results with Camera object
    camera.set_status(status)
    camera.set_report(report)

    return status, report



def get_image_index(filename):
    """ Returns the identity of a filename based on a naming scheme.

    Args:
        filename (str): target filename

    Returns:
        str: identity extracted from filename.
    """
    try:
        identity = index_extractor.match(filename).group(1)
    except AttributeError as err:
        raise AttributeError(f'Unable to extract identity from "{filename}"') from err
    return int(identity)


@torch.no_grad()
def load_image(target_path) -> Image:
    """ Load an image into a Tensor for processing.

    Args:
        target_path (str): path to target image.

    Returns:
        Tensor: image loaded into Tensor for processing.
    """
    try:
        return Image(target_path)
    except ValueError as err:
        logging.debug('Encountered error while loading "%s" --> %s', target_path, err)
        return None


@torch.no_grad()
def analyze_image(target: Image, reference: Image) -> dict:
    """ Analyze a target image with a reference image using a variety of techniques.

    Args:
        target (Image): image to be evaluated.
        reference (Image): image to use as basis of comparison.

    Returns:
        dict: set of scores for each of the evaluation techniques used.
    """
    scores = {
        'brisque_index':    piq.brisque(target.tensor, data_range=1., reduction='none').item(),
        #'dists_loss':       piq.DISTS(reduction='none')(reference, target),
        'ssim_index':       _check_for_similarity(target.tensor, reference.tensor),
        'blur':            _blur_detection(target.image),
    }
    return scores


def _check_for_similarity(target: torch.Tensor, reference: torch.Tensor):
    results = piq.ssim(reference, target)

    return results.item()


def _blur_detection(target):
    image = target
    blur_value = cv2.Laplacian(image, cv2.CV_64F).var()         #pylint: disable=no-member
    return blur_value


def assess_scores(scores: dict) -> bool:
    """ Evaluate scores using a set of threhold based criteria to determine pass/fail status.

    Args:
        scores (dict): Various scores generated by the measure_image function.

    Returns:
        bool: indicates if the scores represent a pass or a failure.
    """
    criteria = [
        scores['brisque_index'] > 0,
        scores['brisque_index'] < 100,
        scores['ssim_index'] > .90,
        scores['blur'] < 80,
        scores['blur'] > 20,
    ]

    return all(criteria)


REFERENCE_IMAGE = load_image(IMAGE_PATH_REFERENCE)
