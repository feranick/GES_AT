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

    # Collect acquisition parameters into a DataFrame to be used for storing (as csv or json)
    def getAcqParameters(self,obj):
        return pd.DataFrame({'operator': [obj.samplewind.operatorText.text()],
                'Acq Min Voltage': [obj.acquisitionwind.minVText.value()],
                'Acq Max Voltage': [obj.acquisitionwind.maxVText.value()],
                'Acq Start Voltage': [obj.acquisitionwind.startVText.value()],
                'Acq Step Voltage': [float(obj.acquisitionwind.stepVText.text())],
                'Acq Num Aver Scans': [obj.acquisitionwind.numAverScansText.value()],
                'Delay Before Meas': [obj.acquisitionwind.delayBeforeMeasText.value()],
                'Num Track Points': [obj.acquisitionwind.numPointsText.value()],
                'Track Interval': [obj.acquisitionwind.IntervalText.value()]})

    def start(self, obj):
        ### Setup interface and get parameters before acquisition
        
        obj.stopAcqFlag = False
        obj.acquisitionwind.enableAcqPanel(False)
        obj.samplewind.enableSamplePanel(False)
        obj.enableButtonsAcq(False)
        QApplication.processEvents()
        self.dfAcqParams = self.getAcqParameters(obj)
        obj.resultswind.clearPlots(True)
        obj.resultswind.show()
        obj.resultswind.setupDataFrame()
        QApplication.processEvents()
        
        for i in range(config.numSubsHolderCol):
            for j in range(config.numSubsHolderRow):
                if obj.samplewind.tableWidget.item(i,j).text() != "":
                    deviceID = obj.samplewind.tableWidget.item(i,j).text()
                    obj.statusBar().showMessage("Acquiring from: " + deviceID + ", " + str(self.dfAcqParams.get_value(0,'Acq Num Aver Scans')) + " sets of JVs", 5000)
                    print("Acquiring from: " + deviceID + ", " + str(self.dfAcqParams.get_value(0,'Acq Num Aver Scans')) + " sets of JVs")
                    obj.resultswind.clearPlots(False)
                    obj.resultswind.setupResultTable()
                    
        ### Acquisition loop should land here ##################
                    
                    self.fakeAcq1(i, j, obj, deviceID, self.dfAcqParams)
        
        ########################################################
                    obj.resultswind.makeInternalDataFrames(i)
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
        VStart = self.dfAcqParams.get_value(0,'Acq Start Voltage')
        VEnd = self.dfAcqParams.get_value(0,'Acq Max Voltage')
        VStep = self.dfAcqParams.get_value(0,'Acq Step Voltage')
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

    def fakeAcq1(self, row, column, obj, deviceID, dfAcqParams):
        timeAcq = 0
        for i in range(self.dfAcqParams.get_value(0,'Num Track Points')):
            if obj.stopAcqFlag is True:
                break
            print("JV #",i+1)
            
            JV = self.generateRandomJV()
            perfData = self.analyseJV(JV)
            perfData = np.hstack((timeAcq, perfData))
            
            obj.resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV)
            
            QApplication.processEvents()
            obj.resultswind.show()
            QApplication.processEvents()
            timeAcq = timeAcq + 1
            time.sleep(1)

    ############  Temporary section ENDS here ###########################



