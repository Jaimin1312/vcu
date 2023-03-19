""" Unittests for vcs.model.images module which covers image loading and processing.
"""
from nose.tools import assert_raises
from testfixtures import LogCapture

from vcs.model import images

PATH_TILE_A1 = r'vcs/tests/assets/ceiling-tile-a1.png'
PATH_TILE_A2 = r'vcs/tests/assets/ceiling-tile-a2.png'
PATH_TILE_B1 = r'vcs/tests/assets/ceiling-tile-b1.png'
PATH_CORRUPTED_IMAGE = r'vcs/tests/assets/corrupted-image.png'
PATH_EMPTY_IMAGE = r'vcs/tests/assets/empty-image.png'

def test_analyze_image():
    """ Test that image analysis generates expected results.
    """
    image = images.load_image(PATH_TILE_A1)
    assert isinstance(image, images.Image), f'type actually is {type(image)}'
    baseline_image = images.load_image(PATH_TILE_A2)
    scores = images.analyze_image(image, baseline_image)

    assert scores['brisque_index'] == 44.59442138671875, scores['brisque_index']
    assert scores['ssim_index'] == 0.9686770439147949, scores['ssim_index']
    assert scores['blur'] == 29.365534976647233, scores['blur']

    assert images.assess_scores(scores) is True, scores


def test_analyze_against_drifted_baseline():
    """ Test that image analysis indicates a drifted baseline.
    NOTE: ssim_index will be below the expected 0.90 threshold which indicates that the
        image is sufficiently different from the baseline to no longer associate it
        with the expected camera position.
    """
    image = images.load_image(PATH_TILE_A1)
    assert isinstance(image, images.Image), f'type actually is {type(image)}'
    baseline_image = images.load_image(PATH_TILE_B1)
    scores = images.analyze_image(image, baseline_image)

    assert scores['brisque_index'] == 44.59442138671875, scores['brisque_index']
    assert scores['ssim_index'] == 0.768852949142456, scores['ssim_index']
    assert scores['blur'] == 29.365534976647233, scores['blur']

    assert images.assess_scores(scores) is False, scores


def test_load_empty_image():
    """ Test that loading an empty image returns as None.
    """
    with LogCapture() as logs:
        image = images.load_image(PATH_EMPTY_IMAGE)
        assert image is None, image
        assert (
            'Could not find a backend to open `vcs/tests/assets/empty-image.png``'
            ' with iomode `ri`.') in str(logs), str(logs)


def test_load_corrupted_image():
    """ Test that loading a corrupted image returns as None.
    """
    with LogCapture() as logs:
        image = images.load_image(PATH_CORRUPTED_IMAGE)
        assert image is None, image
        assert 'Reason: "broken data stream when reading image file"' \
            in str(logs), str(logs)


def test_load_missing_image():
    """ Test that loading a missing image raises a FileNotfoundError.
    """
    with assert_raises(FileNotFoundError):
        images.load_image("made_up_path")


def test_load_baselines():
    """ Test that baseline images can be loaded from assets folder.
    """
    baselines = images.Baselines(images.PATH_TO_BASELINES)
    assert len(baselines) == 8, len(baselines)


def test_get_index_valid():
    """ Test that we can get index for a valid image name.
    """
    index = images.get_image_index('/foo/bar/device3_20220123-123432.jpg')
    assert index == 3, index


def test_get_index_invalid():
    """ Test that we can get index for a valid image name.
    """
    with assert_raises(AttributeError):
        images.get_image_index('/foo/bar/invalid3_20220123-123432.jpg')
