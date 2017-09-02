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

__version__ = "0.2.12"
__author__ = "<qt><a href = mailto:ferralis@mit.edu> Nicola Ferralis</a></qt>"

from .configuration import *
import os.path

config = Configuration()
if os.path.isfile(config.configFile) is False:
    print("Configuration file does not exist: Creating one.")
    config.createConfig()
config.readConfig(config.configFile)

import logging
logging.basicConfig(filename=config.loggingFilename, level=int(config.loggingLevel))
logger = logging.getLogger()

from . import configuration
from . import mainWindow
from . import acquisition
from . import acquisitionWindow
from . import sampleWindow
from . import resultsWindow
from . import cameraWindow
from . import dataManagement
from . import dataManagementWindow
from . import powermeterWindow



