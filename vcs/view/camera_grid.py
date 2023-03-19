"""Camera Grid Tkinter Widget support.

CameraGrid
CameraItem
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, UnidentifiedImageError

from vcs.model.camera import Camera

DEBUG = False
MAX_CAMERA_COUNT = 8
CAMERA_COLUMNS = 2

MAX_IMAGE_WIDTH = 400
MAX_IMAGE_HEIGHT = 210

COLOR_FAIL = 'red'
COLOR_PASS = 'green1'

DEFAULT_TINT_COLOR = (COLOR_PASS)
DEFAULT_TRANSPARENCY = .35
DEFAULT_OPACITY = int(255 * DEFAULT_TRANSPARENCY)
MARK_OUTLINE_WIDTH = 20
MARK_FILLED = False

PAD = 2

class CameraGrid(tk.Frame):
    """ A tkinter widget displaying a grid of camera images.

    Args:
        parent (tk.Widget): container widget
    """
    def __init__(self, parent: tk.Widget, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._images: list[CameraItem] = []

        for index in range(MAX_CAMERA_COUNT):
            item = CameraItem(self, index)
            self._images.append(item)

            # Layout in 2 by 4 grid
            item.grid(column=index%CAMERA_COLUMNS,
                      row=index//CAMERA_COLUMNS,
                      sticky=tk.W, padx=PAD, pady=PAD)

            if DEBUG:
                if index%3 == 1:
                    item.mark(COLOR_PASS)
                if index%3 == 2:
                    item.mark(COLOR_FAIL)

        self.pack()


    def set(self, camera_list: list[Camera]):
        """ Assign a list of images to corresponding camera grid positions.

        Images are provided by the Camera list where each camera is expected to
            have at least one image.
        Position is determined using the 'index' field of each Camera item.

        Args:
            camera_list (list[Camera]): list of cameras to apply to the grid.
        """
        for camera in camera_list:
            self._images[camera.index].set_image(camera.first_image_path)


    def mark_as_pass(self, index):
        """ Highlight a camera as having passed.

        Displays a semi-transparent green frame in front of the image.

        Args:
            index (int): image position.
        """
        self._images[index].mark(COLOR_PASS)


    def mark_as_fail(self, index):
        """ Hightlight a camera as having failed.

        Displays a semi-transparent red frame in front of the image.

        Args:
            index (int): image position.
        """
        self._images[index].mark(COLOR_FAIL)


    def clear(self):
        """ Clears the image and the highlighting for all image positions.
        """
        for camera in self._images:
            camera.set_image()


class CameraItem(tk.Frame):
    """ Tkinter widget for displaying camera images with support for highlighting them to indicate
    pass/fail of related image quality assessment.

    Args:
        parent (tk.Widget): container widget.
        index (int): index of this widget in the parent list.
    """
    def __init__(self, parent: tk.Widget, index: int, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._source_image = None

        name = f"Camera {index+1}"
        self._lf = ttk.LabelFrame(self, text=name)
        self._label = tk.Label(self._lf, width=MAX_IMAGE_WIDTH, height=MAX_IMAGE_HEIGHT)
        self._lf.pack()
        self._label.pack(padx=4, pady=(0,4))

        self.set_image()


    def set_image(self, image_path=None):
        """ Display an image.

        Args:
            image_path (str, optional): path to an image to display. Defaults to None.
        """
        try:
            image = Image.open(image_path)
            resize_ratio = min(MAX_IMAGE_WIDTH/image.width, MAX_IMAGE_HEIGHT/image.height)
            size = (image.width, image.height)
            resized_image = image.resize((round(size[0]*resize_ratio), round(size[1]*resize_ratio)))
            self._source_image = resized_image
        except (AttributeError, UnidentifiedImageError):
            # Create a blank image of the expected size if we are unable to open the given path
            self._source_image = Image.new('RGBA', (MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT))
        self._draw(self._source_image)


    def mark(self, color_name=DEFAULT_TINT_COLOR, opacity=DEFAULT_OPACITY,
             outline_width=MARK_OUTLINE_WIDTH):
        """ Highlight the image with a semi-transparent frame of the provided color.

        Args:
            color_name (str, optional): Color name to use for the highlighted frame.
                Defaults to DEFAULT_TINT_COLOR.
            opacity (float, optional): Percentage of opacity for highlighted frame.
                Defaults to DEFAULT_OPACITY.
            outline_width (int, optional): Width of the semi-transparent outline.
                Defaults to MARK_OUTLINE_WIDTH.
        """
        color = self._rgb(color_name)
        target_image = self._source_image
        overlay = Image.new('RGBA', target_image.size, color+(0,))
        draw = ImageDraw.Draw(overlay)
        fill = color+(opacity,) if MARK_FILLED else None
        draw.rectangle(((0,0), target_image.size),
                       fill=fill,
                       outline=color+(opacity, ),
                       width=outline_width,
                       )
        colored_image = Image.alpha_composite(target_image, overlay)
        self._draw(colored_image)


    def _rgb(self, colorname):
        """ Returns 3-part color tuple for the corresponding colorname.
        """
        return self.winfo_rgb(colorname)


    def _draw(self, image):
        imagetk = ImageTk.PhotoImage(image)
        self._label.config(image=imagetk)
        self._label.image = imagetk
