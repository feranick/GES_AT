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
import configparser, logging, os
from pathlib import Path
from . import __version__

class Configuration():
    def __init__(self):
        self.home = str(Path.home())+"/"
        self.configFile = str(self.home+"GridEdgeAT.ini")
        self.generalFolder = str(self.home+"GridEdgeAT/")
        Path(self.generalFolder).mkdir(parents=True, exist_ok=True)
        self.logFile = str(self.generalFolder+"GridEdgeAT.log")
        self.dataFolder = str(self.generalFolder + 'data/')
        Path(self.dataFolder).mkdir(parents=True, exist_ok=True)
        self.substrateFolder = str(self.generalFolder + 'substrates/')
        Path(self.substrateFolder).mkdir(parents=True, exist_ok=True)
        self.imagesFolder = str(self.generalFolder + 'images/')
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
            'substrateArea' : 6.4516,
            }
    def defineConfAcq(self):
        self.conf['Acquisition'] = {
            'acqSoakVoltage' : 1,
            'acqSoakTime' : 2,
            'acqHoldTime' : 1,
            'acqStepVoltage' : 0.5,
            'acqDirection': 0,
            'acqForwardVoltage' : 1,
            'acqReverseVoltage' : -1,
            'acqArchitecture' : 0,
            'acqDelayBeforeMeas' : 1,
            'acqTrackNumDevices' : 2,
            'acqTrackTime' : 5,
            }
    def defineConfInstr(self):
        self.conf['Instruments'] = {
            'alignmentIntThreshold' : 0.6,
            'alignmentContrastDefault' : 1,
            'alignmentIntMax' : 10,
            'powermeterID' : "USB0::0x1313::0x8072::P2008173::INSTR",
            'irradiance1Sun' : 4.5044,
            'irradianceSensorArea' : 3.24,
            'switchboxID' : "GPIB0::16::INSTR",
            'sourcemeterID' : "GPIB0::24::INSTR",
            'xPosRefCell' : 240,
            'yPosRefCell' : 170,
            }
    def defineConfSystem(self):
        self.conf['System'] = {
            'appVersion' : __version__,
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
        self.sysConfig = self.conf['System']
        self.appVersion = self.sysConfig['appVersion']
        if str(self.appVersion).rsplit('.',1)[0] != __version__.rsplit('.',1)[0] :
            print("Configuration file is for an earlier version of the software")
            oldConfigFile = str(os.path.splitext(configFile)[0]+"_"+str(self.appVersion)+".ini")
            print("Old config file backup: ",oldConfigFile)
            os.rename(configFile, oldConfigFile )
            print("Creating a new config file.")
            self.createConfig()
            
        self.devConfig = self.conf['Devices']
        self.acqConfig = self.conf['Acquisition']
        self.instrConfig = self.conf['Instruments']
        self.sysConfig = self.conf['System']
        self.dmConfig = self.conf['DM']

        self.numSubsHolderRow = self.conf.getint('Devices','numSubsHolderRow')
        self.numSubsHolderCol = self.conf.getint('Devices','numSubsHolderCol')
        self.substrateArea = self.conf.getfloat('Devices','substrateArea')
        
        self.acqSoakVoltage = self.conf.getfloat('Acquisition','acqSoakVoltage')
        self.acqSoakTime = self.conf.getfloat('Acquisition','acqSoakTime')
        self.acqHoldTime = self.conf.getfloat('Acquisition','acqHoldTime')
        self.acqStepVoltage = self.conf.getfloat('Acquisition','acqStepVoltage')
        self.acqDirection = self.conf.getint('Acquisition','acqDirection')
        self.acqForwardVoltage = self.conf.getfloat('Acquisition','acqForwardVoltage')
        self.acqReverseVoltage = self.conf.getfloat('Acquisition','acqReverseVoltage')
        self.acqDelayBeforeMeas = self.conf.getfloat('Acquisition','acqDelayBeforeMeas')
        self.acqArchitecture = self.conf.getint('Acquisition','acqArchitecture')
        self.acqTrackNumDevices = self.conf.getint('Acquisition','acqTrackNumDevices')
        self.acqTrackTime = self.conf.getint('Acquisition','acqTrackTime')

        self.alignmentIntThreshold = self.conf.getfloat('Instruments','alignmentIntThreshold')
        self.alignmentContrastDefault = self.conf.getfloat('Instruments','alignmentContrastDefault')
        self.alignmentIntMax = self.conf.getfloat('Instruments','alignmentIntMax')
        self.powermeterID = self.instrConfig['powermeterID']
        self.irradiance1Sun = self.conf.getfloat('Instruments','irradiance1Sun')
        self.irradianceSensorArea = self.conf.getfloat('Instruments','irradianceSensorArea')
        self.switchboxID = self.instrConfig['switchboxID']
        self.sourcemeterID = self.instrConfig['sourcemeterID']
        self.xPosRefCell = self.conf.getint('Instruments','xPosRefCell')
        self.yPosRefCell = self.conf.getint('Instruments','yPosRefCell')

        self.appVersion = self.sysConfig['appVersion']
        self.loggingLevel = self.sysConfig['loggingLevel']
        self.loggingFilename = self.sysConfig['loggingFilename']
        self.csvSavingFolder = self.sysConfig['csvSavingFolder']
        self.saveLocalCsv = self.conf.getboolean('System','saveLocalCsv')
        
        self.submitToDb = self.conf.getboolean('DM','submitToDb')
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
