'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import numpy as np
import time
from .acquisitionWindow import *
from .resultsWindow import *

class Acquisition():
    def __init__(self):
        self.acqwind = AcquisitionWindow()
        self.resultswind = ResultsWindow()
    
    def getAcqParameters(self):
        self.acqMinVoltage = self.acqwind.minVText.value()
        self.acqMaxVoltage = self.acqwind.maxVText.value()
        self.acqStartVoltage = self.acqwind.startVText.value()
        self.acqStepVoltage = float(self.acqwind.stepVText.text())
        self.acqNumAvScans = self.acqwind.numAverScansText.value()
        self.acqDelBeforeMeas = self.acqwind.delayBeforeMeasText.value()
        self.acqTrackNumPoints = self.acqwind.numPointsText.value()
        self.acqTrackInterval = self.acqwind.IntervalText.value()
    
    def start(self):
        self.getAcqParameters()
        self.time = 0
        print("Acquisition: Start")
        self.resultswind.clearPlots()
        ############  This part is temporary  ###########################
        for i in range(self.acqTrackNumPoints):
            print("JV #",i+1)
            self.resultswind.processData(self.time, self.generateRandomJV())
            time.sleep(2)
            self.resultswind.show()
            self.time = self.time + 1
        ############  This part is temporary  ###########################
        print("Acquisition: Done")
        
    def stop(self, obj):
        obj.statusBar().showMessage("Not yet implemented", 5000)
        print("Not yet implemented")

    ################################################################
    def generateRandomJV(self):
        VStart = self.acqStartVoltage
        VEnd = self.acqMaxVoltage
        VStep = self.acqStepVoltage
        I0 = 1e-10
        Il = 0.5
        n = 1 + random.randrange(0,20,1)/10
        T = 300
        kB = 1.38064852e-23  # Boltzman constant m^2 kg s^-2 K^-1
        q = 1.60217662E-19  # Electron charge
        
        JV = np.zeros((0,2))
        for i in np.arange(VStart,VEnd,VStep):
            temp = Il - I0*math.exp(q*i/(n*kB*T))
            JV = np.vstack([JV,[i,temp]])
        JV[:,1] = JV[:,1]-np.amin(JV[:,1])
        return JV

    ### This will only be used for testing, to sumulate an actual experiment
    def temporaryAcquisition(self):
        self.resultswind.time = self.resultswind.time + 1
        self.resultswind.processData(self.generateRandomJV())
