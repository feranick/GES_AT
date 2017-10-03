'''
configuration
------------------
Class for handling configuration

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import configparser, logging
from pathlib import Path

class Configuration():
    def __init__(self):
        self.home = str(Path.home())+"/"
        self.configFile = str(self.home+"GridEdgeAT.ini")
        self.generalFolder = str(self.home+"/GridEdgeAT/")
        Path(self.generalFolder).mkdir(parents=True, exist_ok=True)
        self.logFile = str(self.generalFolder+"GridEdgeAT.log")
        self.dataFolder = str(self.generalFolder + '/data')
        Path(self.dataFolder).mkdir(parents=True, exist_ok=True)
        self.substrateFolder = str(self.generalFolder + '/substrates')
        Path(self.substrateFolder).mkdir(parents=True, exist_ok=True)
        self.imagesFolder = str(self.generalFolder + '/images/')
        Path(self.imagesFolder).mkdir(parents=True, exist_ok=True)
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = str
    
    # Create configuration file
    def createConfig(self):
        try:
            self.defineConfDevices()
            self.defineConfAcq()
            self.defineConfInstr()
            self.defineConfSystem()
            self.defineConfDM()
            with open(self.configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in creating configuration file")

    # Hadrcoded default definitions for the confoguration file
    def defineConfDevices(self):
        self.conf['Devices'] = {
            'numSubsHolderRow' : 4,
            'numSubsHolderCol' : 4,
            }
    def defineConfAcq(self):
        self.conf['Acquisition'] = {
            'acqSoakVoltage' : 1,
            'acqSoakTime' : 1,
            'acqHoldTime' : 1,
            'acqStepVoltage' : 0.02,
            'acqDirection': 0,
            'acqReverseVoltage' : -1,
            'acqForwardVoltage' : 1,
            'acqArchitecture' : 0,
            'acqTrackNumDevices' : 2,
            'acqTrackTime' : 20,
            }
    def defineConfInstr(self):
        self.conf['Instruments'] = {
            'alignmentIntThreshold' : 0.6,
            'alignmentContrastDefault' : 1,
            'alignmentIntMax' : 10,
            'powermeterID' : "USB0::0x1313::0x8072::P2008173::INSTR",
            'irradiance1Sun' : 3682,
            'switchboxID' : "GPIB0::16::INSTR",
            'sourcemeterID' : "GPIB0::24::INSTR",
            }
    def defineConfSystem(self):
        self.conf['System'] = {
            'loggingLevel' : logging.INFO,
            'loggingFilename' : self.logFile,
            'csvSavingFolder' : self.dataFolder,
            'saveLocalCsv' : False,
            }
    def defineConfDM(self):
        self.conf['DM'] = {
            'submitToDb' : True,
            'DbHostname' : "18.82.1.200",
            'DbPortNumber' : "27017",
            'DbName' : "test",
            'DbUsername' : "user",
            'DbPassword' : "Tata",
            'DbHttpPortNumber' : "3000",
            'DbHttpPath' : "/api/Measurements",
            }

    # Read configuration file into usable variables
    def readConfig(self, configFile):
        self.conf.read(configFile)
        self.devConfig = self.conf['Devices']
        self.acqConfig = self.conf['Acquisition']
        self.instrConfig = self.conf['Instruments']
        self.sysConfig = self.conf['System']
        self.dmConfig = self.conf['DM']

        self.numSubsHolderRow = eval(self.devConfig['numSubsHolderRow'])
        self.numSubsHolderCol = eval(self.devConfig['numSubsHolderCol'])
        
        self.acqSoakVoltage = eval(self.acqConfig['acqSoakVoltage'])
        self.acqSoakTime = eval(self.acqConfig['acqSoakTime'])
        self.acqHoldTime = eval(self.acqConfig['acqHoldTime'])
        self.acqStepVoltage = eval(self.acqConfig['acqStepVoltage'])
        self.acqDirection = eval(self.acqConfig['acqDirection'])
        self.acqReverseVoltage = eval(self.acqConfig['acqReverseVoltage'])
        self.acqForwardVoltage = eval(self.acqConfig['acqForwardVoltage'])
        self.acqArchitecture = eval(self.acqConfig['acqArchitecture'])
        self.acqTrackNumDevices = eval(self.acqConfig['acqTrackNumDevices'])
        self.acqTrackTime = eval(self.acqConfig['acqTrackTime'])

        self.alignmentIntThreshold = eval(self.instrConfig['alignmentIntThreshold'])
        self.alignmentContrastDefault = eval(self.instrConfig['alignmentContrastDefault'])
        self.alignmentIntMax = eval(self.instrConfig['alignmentIntMax'])
        self.powermeterID = self.instrConfig['powermeterID']
        self.irradiance1Sun = eval(self.instrConfig['irradiance1Sun'])
        self.switchboxID = self.instrConfig['switchboxID']
        self.sourcemeterID = self.instrConfig['sourcemeterID']

        self.loggingLevel = self.sysConfig['loggingLevel']
        self.loggingFilename = self.sysConfig['loggingFilename']
        self.csvSavingFolder = self.sysConfig['csvSavingFolder']
        self.saveLocalCsv = eval(self.sysConfig['saveLocalCsv'])
        self.submitToDb = eval(self.dmConfig['submitToDb'])
        self.DbHostname = self.dmConfig['DbHostname']
        self.DbPortNumber = self.dmConfig['DbPortNumber']
        self.DbName = self.dmConfig['DbName']
        self.DbUsername = self.dmConfig['DbUsername']
        self.DbPassword = self.dmConfig['DbPassword']
        self.DbHttpPortNumber = self.dmConfig['DbHttpPortNumber']
        self.DbHttpPath = self.dmConfig['DbHttpPath']

    # Save current parameters in configuration file
    def saveConfig(self, configFile):
        try:
            with open(configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in saving parameters")
