"""
gridedgeat.io
-------------

Import routines for different file formats

"""

import numpy as np
from .qt import QtGui as qtgui

# load regular expression package (for parsing of energy from file name)
import re
import os.path

from . import logger

#### load packages for available file types ####
formats_available = []
# try to import PIL in two possible ways (dependent on PIL version)
try:
    from PIL import Image
    formats_available.append("PIL")
except:
    try:
        import Image
        formats_available.append("PIL")
    except:
        logger.warning("The pillow package is not installed.")

class ImageLoader(object):
    """ Abstract base class for a class loading LEED images.

    Subclasses need to provide
        - get_image(image_path)

    Subclasses may override (default: from filename with regex)
        - get_energy(image_path)
    """
    def __init__(self, image_paths, regex):
        # build a dictionary with energy as key and imagePath as value
        self.regex = regex
        self.files = {}


class PILImageLoader(ImageLoader):
    """ Load image files supported by Python Imaging Library (PIL). """

    extensions = ["tif", "tiff", "png", "jpg", "bmp"]

    @staticmethod
    def get_image(image_path):
        im = Image.open(image_path)
        data = np.asarray(im.convert('L'), dtype=np.uint16)
        return data

class ImageFormat:
    """ Class describing an image format. """
    def __init__(self, abbrev, loader):
        """
        abbrev: abbreviation (e.g. FITS)
        loader: ImageLoader subclass for this format
        """
        self.abbrev = abbrev
        self.loader = loader
        self.extensions = loader.extensions

    def __str__(self):
        return "{0}-Files ({1})".format(self.abbrev, " ".join(self.extensions))

    def extensions_wildcard(self):
        return ['*.%s' % ext for ext in self.extensions]

""" Dictionary of available ImageFormats. """
IMAGE_FORMATS = [format_ for format_ in \
                    [ImageFormat("PIL", PILImageLoader)] \
                         if format_.abbrev in formats_available]

class AllImageLoader(ImageLoader):

    @staticmethod
    def supported_extensions():
        extensions = []
        for image_format in IMAGE_FORMATS:
            extensions.extend(image_format.extensions_wildcard())
        return extensions

    def get_image(self, image_path):
        extension = os.path.splitext(image_path)[1][1:]
        for image_format in IMAGE_FORMATS:
            loader = image_format.loader
            if extension in loader.extensions:
                return loader.get_image(image_path)
        raise IOError('The filetype is not supported')

