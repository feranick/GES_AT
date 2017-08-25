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

## Sample holder parameters ##
numSubsHolderRow = 4
numSubsHolderCol = 4

## Acquisition parameters ##
# Steady state measurements #
acqMinVoltage = 0
acqMaxVoltage = 1
acqStartVoltage = 0
acqStepVoltage = 0.02
acqNumAvScans = 5
acqDelBeforeMeas = 1
#Tracking
acqTrackNumPoints = 5
acqTrackInterval = 2

## Camera related parameter ##
# Threshold for contrast in camera alignment
alignmentIntThreshold = 0.6
# if contrast ratio is larger than this value, devices/masks are
# misalligned
alignmentContrastDefault = 1
# if max intenity is larger than this value, the requirement for
# intensity is satisfied for checing the alignment
alignmentIntMax = 10

## Powermeter related parameters ##
powermeterID = "USB0::0x1313::0x8072::P2008173::INSTR"

## Data-management interaction ##
DbHostname = "18.82.1.200"
DbPortNumber = "27017"
DbName = "test"
DbUsername = "user"
DbPassword = "Tata"

