"""
AARTY: Advanced ASCII Art Rendering Toolkit in Python

A framework for rendering images in terminals/TTYs with support for colors, custom symbol sets,
and various rendering options.
"""

from .color import ANSIColor
from .symbols import Symbols, EMPTY_SET, EMPTY_CHAR
from .config import Config, COLORS, REVERSE
from .text_image import TextImage, Fragment, IndexedFragment
from .converter import convert_image_to_ascii, PixelImage, FragmentWriter

__version__ = "0.7.0"