
from vcs.model.camera import Camera, assign_images_to_cameras


def test_camera_report_message():
    """ Test that the Camera report message includes expected details.
    """
    camera = Camera(5, '012345')
    message_pre_report = camera.get_status_message()
    camera.set_report({'blur':1.2345,'ssim_index':4.5612})
    camera.set_status(True)
    message_post_report_pass = camera.get_status_message()
    camera.set_status(False)
    message_post_report_fail = camera.get_status_message()

    assert message_pre_report == '    Camera 6:\tn/a --> ', message_pre_report
    assert message_post_report_pass == \
        '    Camera 6:	pass --> blur=1.23, ssim_index=4.56', message_post_report_pass
    assert message_post_report_fail == \
        '    Camera 6:	fail --> blur=1.23, ssim_index=4.56', message_post_report_fail


def test_assign_images_to_cameras():
    """ Test that assign_images_to_cameras can correctly parse a directory of images
    """
    cameras = [Camera(index, '') for index in range(8)]
    camera_to_device_lookup = {
        0:7,
        1:6,
        2:5,
        3:4,
        4:3,
        5:2,
        6:1,
        7:0,
    }
    assert cameras[0].first_image_path is None, cameras[0].images

    assign_images_to_cameras(cameras, 'assets/baseline-images', camera_to_device_lookup)
    assert 'device7' in cameras[0].first_image_path, cameras[0].images
    assert 'device3' in cameras[4].first_image_path, cameras[4].images
    assert 'device0' in cameras[7].first_image_path, cameras[7].images

    assert len(cameras[0].images) == 1, len(cameras[0].images)


def test_camera_has_expected_images():
    """ Test that camera reports as having the expected number of images depending on
    whether or not the serial number had been set.

    Images with a serial number are expected to have an image.
    Images without a serial number are expected to not have an image.

    Used as a determiniation of whether to highlight camera as a failure.
    """
    camera_with_serial_number = Camera(0, "01234")
    camera_without_serial_number = Camera(0, "")

    assert camera_with_serial_number.has_expected_images is False
    assert camera_without_serial_number.has_expected_images is True

    camera_with_serial_number.associate_image_path("foo/bar.png")
    camera_without_serial_number.associate_image_path("foo/bar.png")

    assert camera_with_serial_number.has_expected_images is True
    assert camera_without_serial_number.has_expected_images is False
