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
import time, random, math, threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication)
from PyQt5.QtCore import (QObject, QThread, pyqtSlot, pyqtSignal)
from .acquisitionWindow import *
from . import logger

class Acquisition():    
    # Collect acquisition parameters into a DataFrame to be used for storing (as csv or json)
    def getAcqParameters(self,obj):
        self.numRow = int(obj.config.numSubsHolderRow)
        self.numCol = int(obj.config.numSubsHolderCol)
        pdframe = pd.DataFrame({'Operator': [obj.samplewind.operatorText.text()],
                'Acq Min Voltage': [float(obj.acquisitionwind.minVText.text())],
                'Acq Max Voltage': [float(obj.acquisitionwind.maxVText.text())],
                'Acq Start Voltage': [float(obj.acquisitionwind.startVText.text())],
                'Acq Step Voltage': [float(obj.acquisitionwind.stepVText.text())],
                'Acq Num Aver Scans': [float(obj.acquisitionwind.numAverScansText.text())],
                'Delay Before Meas': [float(obj.acquisitionwind.delayBeforeMeasText.text())],
                'Num Track Points': [int(obj.acquisitionwind.numPointsText.value())],
                'Track Interval': [float(obj.acquisitionwind.IntervalText.text())],
                'Comments': [obj.samplewind.commentsText.text()]})
        return pdframe[['Acq Min Voltage','Acq Max Voltage','Acq Start Voltage',
                'Acq Step Voltage','Acq Num Aver Scans','Delay Before Meas',
                'Num Track Points','Track Interval','Operator','Comments']]
                
    def start(self, obj):
        ### Setup interface and get parameters before acquisition
        
        obj.stopAcqFlag = False
        obj.acquisitionwind.enableAcqPanel(False)
        obj.samplewind.resetCellAcq()
        obj.samplewind.enableSamplePanel(False)
        obj.enableButtonsAcq(False)
        QApplication.processEvents()
        self.dfAcqParams = self.getAcqParameters(obj)
        obj.resultswind.clearPlots(True)
        obj.resultswind.show()
        obj.resultswind.setupDataFrame()
        QApplication.processEvents()
        
        for i in range(self.numCol):
            for j in range(self.numRow):
                if obj.samplewind.tableWidget.item(i,j).text() != "":
                    deviceID = obj.samplewind.tableWidget.item(i,j).text()
                    operator = obj.samplewind.operatorText.text()
                    msg = "Operator: " + operator
                    print(msg)
                    logger.info(msg)
                    msg = "Acquisition started: "+self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]

                    print(msg)
                    logger.info(msg)
                    msg = "Acquiring from: " + deviceID + " - substrate("+str(i)+", "+str(j)+")"
                    obj.statusBar().showMessage(msg, 5000)
                    print(msg)
                    logger.info(msg)
                    obj.resultswind.clearPlots(False)
                    obj.resultswind.setupResultTable()
                    obj.samplewind.colorCellAcq(i,j,"red")
                    
        ### Acquisition loop should land here ##################
                    
                    #self.fakeAcq(i, j, obj, deviceID, self.dfAcqParams)
                    self.get_thread = acqThread(self.dfAcqParams)
                    #self.get_thread.JVcomplete.connect(lambda: self.processFakeAcq(JV, obj, self.deviceID, self.dfAcqParams))
                    self.get_thread.done.connect(self.printmsg)
                    self.get_thread.start()
        
        ########################################################
                    obj.resultswind.makeInternalDataFrames(obj.resultswind.lastRowInd,
                        obj.resultswind.deviceID,obj.resultswind.perfData,
                        obj.resultswind.JV1)
                    obj.samplewind.colorCellAcq(i,j,"green")
        msg = "Acquisition Completed: "+ self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]
        obj.acquisitionwind.enableAcqPanel(True)
        obj.samplewind.enableSamplePanel(True)
        obj.enableButtonsAcq(True)
        obj.statusBar().showMessage(msg, 5000)
        print(msg)
        logger.info(msg)
    
    def printmsg(self, msg):
        print(msg)
        
    def stop(self, obj):
        msg = "Acquisition stopped: " + self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]
        obj.statusBar().showMessage(msg, 5000)
        obj.stopAcqFlag = True
        print(msg)
        logger.info(msg)
    
    def analyseJV(self, powerIn, JV):
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        Voc = JV[JV.shape[0]-1,0]
        Jsc = JV[0,1]
        Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
        Jpmax = JV[np.where(PV == np.amax(PV)),1][1][0]
        FF = Vpmax*Jpmax*100/(Voc*Jsc)
        effic = Vpmax*Jpmax/powerIn
        data = np.array([Voc, Jsc, Vpmax*Jpmax,FF,effic])
        return data
        
    def getDateTimeNow(self):
        return str(datetime.now().strftime('%Y-%m-%d')), str(datetime.now().strftime('%H-%M-%S'))
    
    ############  Temporary section STARTS here ###########################
    def generateRandomJV(self, dfAcqParams):
        VStart = dfAcqParams.get_value(0,'Acq Start Voltage')
        VEnd = dfAcqParams.get_value(0,'Acq Max Voltage')
        VStep = dfAcqParams.get_value(0,'Acq Step Voltage')
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

    def fakeAcq(self, row, column, obj, deviceID, dfAcqParams):
        timeAcq = 0
        # Add device number to substrate
        # this is totally to fake the cquisition of a particular device in a batch
        #new_deviceID = deviceID+str(random.randrange(1,7,1)) # Use this for completely random device number
        new_deviceID = deviceID+"4"  # Use this temporarily for pushing data through DM via POST
        
        for i in range(self.dfAcqParams.get_value(0,'Num Track Points')):
            if obj.stopAcqFlag is True:
                break
            msg = "Scan #"+str(i+1)
            print(msg)
            logger.info(msg)
            
            JV = self.devFakeAcq()

            perfData = self.analyseJV(float(obj.config.conf['Instruments']['powerIn1Sun']),JV)
            perfData = np.hstack((timeAcq, perfData))
            perfData = np.hstack((self.getDateTimeNow()[1], perfData))
            perfData = np.hstack((self.getDateTimeNow()[0], perfData))
            print('%s, %s,' % (threading.current_thread().name,
                              threading.current_thread().ident))
            
                              
                              
            obj.resultswind.processDeviceData(new_deviceID, dfAcqParams, perfData, JV)
            
            #QApplication.processEvents()
            obj.resultswind.show()
            #QApplication.processEvents()
            timeAcq = timeAcq + 1
            time.sleep(1)



    def devFakeAcq(self):
            try:
                JV = self.generateRandomJV()
            except:
                msg = "Check your acquisition settings (Start Voltage)"
                print(msg)
                logger.info(msg)
                return 0
            return JV

    def processFakeAcq(self, JV, obj, deviceID, dfAcqParams):
        timeAcq = 0
        # Add device number to substrate
        # this is totally to fake the cquisition of a particular device in a batch
        new_deviceID = deviceID+str(random.randrange(1,7,1)) # Use this for completely random device number

        perfData = self.analyseJV(float(obj.config.conf['Instruments']['powerIn1Sun']),JV)
        perfData = np.hstack((timeAcq, perfData))
        perfData = np.hstack((self.getDateTimeNow()[1], perfData))
        perfData = np.hstack((self.getDateTimeNow()[0], perfData))

        obj.resultswind.processDeviceData(new_deviceID, dfAcqParams, perfData, JV)
            
        QApplication.processEvents()
        obj.resultswind.show()
        QApplication.processEvents()
        timeAcq = timeAcq + 1
        time.sleep(1)


    ############  Temporary section ENDS here ###########################
    
class acqThread(QThread):

    JVcomplete = pyqtSignal(np.ndarray)
    done = pyqtSignal(str)
    
    def __init__(self, dfAcqParams):
        """
        Make a new thread instance with the specified
        subreddits as the first argument. The subreddits argument
        will be stored in an instance variable called subreddits
        which then can be accessed by all other class instance functions

        :param subreddits: A list of subreddit names
        :type subreddits: list
        """
        QThread.__init__(self)
        self.dfAcqParams = dfAcqParams

    def __del__(self):
        self.wait()

    def devFakeAcq(self):
        print("Creating JV")
        ac = Acquisition()
        JV = ac.generateRandomJV(self.dfAcqParams)
        del ac
        return JV

    def run(self):
        for i in range(self.dfAcqParams.get_value(0,'Num Track Points')):
            msg = "Scan #"+str(i+1)
            print(msg)
            logger.info(msg)
            
            JV = self.devFakeAcq()
            #self.emit(SIGNAL('processFakeAcq(JV, obj, self.deviceID, self.dfAcqParams)'), JV)
            self.done.emit('Done with Thread!')
            #self.JVcomplete.emit(JV)


