'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import numpy as np
import pandas as pd
import time, random, math
from .acquisitionWindow import *

class Acquisition():
    
    def getAcqParameters(self,obj):
        self.acqMinVoltage = obj.acquisitionwind.minVText.value()
        self.acqMaxVoltage = obj.acquisitionwind.maxVText.value()
        self.acqStartVoltage = obj.acquisitionwind.startVText.value()
        self.acqStepVoltage = float(obj.acquisitionwind.stepVText.text())
        self.acqNumAvScans = obj.acquisitionwind.numAverScansText.value()
        self.acqDelBeforeMeas = obj.acquisitionwind.delayBeforeMeasText.value()
        self.acqTrackNumPoints = obj.acquisitionwind.numPointsText.value()
        self.acqTrackInterval = obj.acquisitionwind.IntervalText.value()
        #self.deviceID = obj.samplewind.tableWidget.item(0,0).text()
        self.operatorID = obj.samplewind.operatorText.text()
        #self.inputParams = pd.DataFrame({'device': [self.deviceID], 'operator': [self.operatorID]})
        #self.inputParams = self.inputParams[['operator','device']]

    def start(self, obj):
        ### Setup interface and get parameters before acquisition
        
        obj.stopAcqFlag = False
        obj.acquisitionwind.enableAcqPanel(False)
        obj.samplewind.enableSamplePanel(False)
        obj.enableButtonsAcq(False)
        QApplication.processEvents()
        self.getAcqParameters(obj)
        obj.resultswind.clearPlots()
        obj.resultswind.show()
        QApplication.processEvents()
        
        for i in range(config.numSubsHolderCol):
            for j in range(config.numSubsHolderRow):
                if obj.samplewind.tableWidget.item(i,j).text() != "":
                    deviceID = obj.samplewind.tableWidget.item(0,0).text()
                    obj.statusBar().showMessage("Acquiring from: " + deviceID + ", " + str(self.acqNumAvScans) + " sets of JVs", 5000)
                    print("Acquiring from: " + deviceID + ", " + str(self.acqNumAvScans) + " sets of JVs")
                    inputParams = pd.DataFrame({'device': [deviceID], 'operator': [self.operatorID]})
                    inputParams = inputParams[['operator','device']]
                    
        ### Acquisition loop should land here ###############
                    
                    self.fakeAcq1(obj, inputParams)
        
        #####################################################
        
        print("Acquisition: Completed")
        obj.acquisitionwind.enableAcqPanel(True)
        obj.samplewind.enableSamplePanel(True)
        obj.enableButtonsAcq(True)
        obj.statusBar().showMessage("Acquisition completed", 5000)
        
    def stop(self, obj):
        obj.statusBar().showMessage("Acquisition stopped", 5000)
        obj.stopAcqFlag = True
        print("Acquisition stopped")
    
    def analyseJV(self, JV):
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        Voc = JV[JV.shape[0]-1,0]
        Jsc = JV[0,1]
        Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
        Jpmax = JV[np.where(PV == np.amax(PV)),1][1][0]
        FF = Vpmax*Jpmax*100/(Voc*Jsc)
        data = np.array([Voc, Jsc, FF,Vpmax*Jpmax])
        return data
    
    ############  Temporary section STARTS here ###########################
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

    def fakeAcq1(self, obj, inputParams):
        timeAcq = 0
        for i in range(self.acqTrackNumPoints):
            if obj.stopAcqFlag is True:
                break
            print("JV #",i+1)
            
            JV = self.generateRandomJV()
            perfData = self.analyseJV(JV)
            perfData = np.hstack((timeAcq, perfData))
            
            obj.resultswind.processData(inputParams, perfData, JV)
            
            QApplication.processEvents()
            obj.resultswind.show()
            QApplication.processEvents()
            timeAcq = timeAcq + 1
            time.sleep(1)

    ############  Temporary section ENDS here ###########################



