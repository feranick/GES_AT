'''
initialization.py
-----------------
Initialization of the GridEdge Auto-testing app

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

__version__ = "0.0.9"
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

from . import mainWindow
from . import acquisition
from . import acquisitionWindow
from . import sampleWindow
from . import resultsWindow
from . import cameraWindow
from . import dataManagement



