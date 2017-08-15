'''
default configuration
----------------------
Default configuration parameters

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

# how much information shall be logged
import logging
loggingLevel = logging.INFO
loggingFilename = "gridedgeat.log"

import numpy as np

#### IO related ####
####################

## Camera related parameter ##
# Threshold for contrast in camera alignment
alignmentIntThreshold = 0.6
# if contrast ratio is larger than this value, devices/masks are
# misalligned
alignmentContrastDefault = 1
# if max intenity is larger than this value, the requirement for
# intensity is satisfied for checing the alignment
alignmentIntMax = 10

## Data-management interaction ##
DbHostname = "18.62.7.9"
DbPortNumber = "7101"
DbName = "Tata"
DbUsername = "user1"
DbPassword = "user1"
