'''
configuration
------------------
Class for handling configuration

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import configparser, logging

class Configuration():
    def __init__(self):
        self.configFile = "ges.ini"
        self.conf = configparser.ConfigParser()
    
    def createConfig(self):
        self.conf['Devices'] = {
            'numSubsHolderRow' : 4,
            'numSubsHolderCol' : 4
            }
        self.conf['Acquisition'] = {
            'acqMinVoltage' : 0,
            'acqMaxVoltage' : 1,
            'acqStartVoltage' : 0,
            'acqStepVoltage' : 0.02,
            'acqNumAvScans' : 5,
            'acqDelBeforeMeas' : 1,
            'acqTrackNumPoints' : 5,
            'acqTrackInterval' : 2
            }
        self.conf['Instruments'] = {
            'alignmentIntThreshold' : 0.6,
            'alignmentContrastDefault' : 1,
            'alignmentIntMax' : 10,
            'powermeterID' : "USB0::0x1313::0x8072::P2008173::INSTR"
            }
        self.conf['System'] = {
            'loggingLevel' : logging.INFO,
            'loggingFilename' : "gridedgeat.log",
            'csvSavingFolder' : ".",
            'saveLocalCsv' : True,
            'DbHostname' : "18.82.1.200",
            'DbPortNumber' : "27017",
            'DbName' : "test",
            'DbUsername' : "user",
            'DbPassword' : "Tata"
            }
        with open(self.configFile, 'w') as configfile:
            self.conf.write(configfile)

    def readConfig(self):
        self.conf.read(self.configFile)
        self.devConfig = self.conf['Devices']
        self.acqConfig = self.conf['Acquisition']
        self.instrConfig = self.conf['Instruments']
        self.sysConfig = self.conf['System']

        self.numSubsHolderRow = self.devConfig['numSubsHolderRow']
        self.numSubsHolderCol = self.devConfig['numSubsHolderCol']
        
        self.acqMinVoltage = self.acqConfig['acqMinVoltage']
        self.acqMaxVoltage = self.acqConfig['acqMaxVoltage']
        self.acqStartVoltage = self.acqConfig['acqStartVoltage']
        self.acqStepVoltage = self.acqConfig['acqStepVoltage']
        self.acqNumAvScans = self.acqConfig['acqNumAvScans']
        self.acqDelBeforeMeas = self.acqConfig['acqDelBeforeMeas']
        self.acqTrackNumPoints = self.acqConfig['acqTrackNumPoints']
        self.acqTrackInterval = self.acqConfig['acqTrackInterval']

        self.alignmentIntThreshold = self.instrConfig['alignmentIntThreshold']
        self.alignmentContrastDefault = self.instrConfig['alignmentContrastDefault']
        self.alignmentIntMax = self.instrConfig['alignmentIntMax']
        self.powermeterID = self.instrConfig['powermeterID']

        self.loggingLevel = self.sysConfig['loggingLevel']
        self.loggingFilename = self.sysConfig['loggingFilename']
        self.csvSavingFolder = self.sysConfig['csvSavingFolder']
        self.saveLocalCsv = self.sysConfig['saveLocalCsv']
        self.DbHostname = self.sysConfig['DbHostname']
        self.DbName = self.sysConfig['DbName']
        self.DbUsername = self.sysConfig['DbUsername']
        self.DbPassword = self.sysConfig['DbPassword']

    def saveConfig(self):
        self.conf['Devices'] = self.devConfig
        self.conf['Acquisition'] = self.acqConfig
        self.conf['Instruments'] = self.instrConfig
        self.conf['System'] = self.sysConfig
        with open(self.configFile, 'w') as configfile:
            self.conf.write(self.configfile)




