""" 
The GridEdgeAT package is divided into several subpackages:

- io: Input/Output functionality
- gui: Graphical User Interface

.. automodule:: gridedgeat.gui
    :members:

"""

__version__ = "0.0-preview"
__author__ = "Nicola Ferralis"

# import packages
# order of loading is important and should not be changed
try:
    import sys
    sys.path.append('..')
    import config
except:
    from . import defaultconfig as config

import logging
logging.basicConfig(filename=config.loggingFilename, level=config.loggingLevel)
logger = logging.getLogger()

from . import qt
from . import gui
