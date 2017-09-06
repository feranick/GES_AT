'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Tony Wu <tonyw@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import numpy as np
import pandas as pd
import time, random, math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication,QAbstractItemView)
from PyQt5.QtCore import (QObject, QThread, pyqtSlot, pyqtSignal)
from .acquisitionWindow import *
from . import logger
from .modules.xystage.xystage import *
from .modules.sourcemeter.sourcemeter import *
from .modules.switchbox.switchbox import *

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
        self.obj = obj
        self.dfAcqParams = self.getAcqParameters(obj)
        #JV = np.zeros((0,2))
        ### Setup interface and get parameters before acquisition
        obj.stopAcqFlag = False
        obj.acquisitionwind.enableAcqPanel(False)
        obj.samplewind.resetCellAcq()
        obj.samplewind.enableSamplePanel(False)
        obj.enableButtonsAcq(False)
        QApplication.processEvents()
        obj.resultswind.clearPlots(True)
        
        self.acq_thread = acqThread(self, self.numRow, self.numCol, self.dfAcqParams)
        self.acq_thread.acqJVComplete.connect(lambda JV,deviceID: self.JVDeviceProcess(JV, deviceID, self.dfAcqParams, 1))
        self.acq_thread.done.connect(self.printMsg)
        self.acq_thread.maxPowerDev.connect(self.printMsg)
        self.acq_thread.start()

    # Action for stop button
    def stop(self, obj):
        msg = "Acquisition stopped: " + self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]
        obj.stopAcqFlag = True
        self.printMsg(msg)
    
    # Extract parameters from JV
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
    
    # Get date/time
    def getDateTimeNow(self):
        return str(datetime.now().strftime('%Y-%m-%d')), str(datetime.now().strftime('%H-%M-%S'))

    # Show message on log and terminal
    def printMsg(self, msg):
        print(msg)
        logger.info(msg)
    
    # Convert coordinates as in the Sample Windown Table into the
    # correct substrate number as defined in xystage.py
    def getSubstrateNumber(self, i,j):
        if i > 3 or j > 3:
            print("indexes outside boundaries, resetting to substrate 1")
            return 1
        else:
            return int((4-i)*4-(3-j))
    
    # New version to adapt to changes in Joel's stage code
    # Conversion between device naming is no longer needed.
    ## low level api
    # xy substrate layout (default)
    # column:  1 ==> 4     row:
    # 13 | 14 | 15 | 16     4
    # 9  | 10 | 11 | 12     3
    # 5  | 6  | 7  | 8      2
    # 1  | 2  | 3  | 4      1
    # xy device layout (default)
    # |   ----   |
    # | 1 |  | 4 |
    # | 2 |  | 5 |
    # | 3 |  | 6 |
    # |   ----   |
    
    # pcb substrate layout
    # 1  | 2  | 3  | 4  (-3*4)
    # 5  | 6  | 7  | 8  (-1*4)
    # 9  | 10 | 11 | 12 (+1*4)
    # 13 | 14 | 15 | 16 (+3*4)
    # pcb device layout (default)
    # |   ----   |
    # | 1 |  | 4 |
    # | 2 |  | 5 |
    # | 3 |  | 6 |
    # |   ----   |
    
    def get_pcb_id(self, i,j, xy_dev_id):
        "ID converison between xy to pcb"
        return int((4-i)*4-(3-j)), xy_dev_id

    def switch_device(self, i,j, dev_id):
        "Switch operation devices"
        #self.xy_stage.move_to_device_3x2(sub_id, dev_id)
        self.switch_box.connect(*self.get_pcb_id(i,j, dev_id))
    
    ## measurements: JV
    # obj2: self.source_meter
    # dfAcqParams : self.dfAcqParams
    def measure_JV(self, obj2, dfAcqParams):
        #self.source_meter.set_mode('VOLT')
        obj2.set_mode('VOLT')
        obj2.on()

        # measurement parameters
        v_min = float(dfAcqParams.get_value(0,'Acq Min Voltage'))
        v_max = float(dfAcqParams.get_value(0,'Acq Max Voltage'))
        v_start = float(dfAcqParams.get_value(0,'Acq Start Voltage'))
        v_step = float(dfAcqParams.get_value(0,'Acq Step Voltage'))
        scans = int(dfAcqParams.get_value(0,'Acq Num Aver Scans'))
        hold_time = float(dfAcqParams.get_value(0,'Delay Before Meas'))

        # enforce
        if v_start < v_min and v_start > v_max and v_min > v_max:
            raise ValueError('Voltage Errors')

        # create list of voltage to measure
        v_list = np.arange(v_min-2., v_max + 2., v_step)
        v_list = v_list[np.logical_and(v_min-1e-9 <= v_list, v_list <= v_max+1e-9)]
        start_i = np.argmin(abs(v_start - v_list))

        N = len(v_list)
        i_list = list(range(0, N))[::-1] + list(range(0, N))
        i_list = i_list[N-start_i-1:] + i_list[:N-start_i-1]

        # create data array
        data = np.zeros((N, 3))
        data[:, 0] = v_list

        # measure
        for n in range(scans):
            for i in i_list:
                obj2.set_output(voltage = v_list[i])
                time.sleep(hold_time)
                data[i, 2] += 1.
                data[i, 1] = (obj2.read_values()[1] + data[i,1]*(data[i,2]-1)) / data[i,2]
                #np.savetxt(filename, data[:, 0:2], delimiter=',', header='V,J')

        return data[:, 0:2]

    ## measurements: voc, jsp, mpp
    # obj: self.source_meter
    def measure_voc_jsc_mpp(self, obj2, v_step, hold_time, powerIn):
        # voc
        obj2.set_mode('CURR')
        obj2.on()
        obj2.set_output(current = 0.)
        voc = obj2.read_values()[0]

        # jsc
        obj2.set_mode('VOLT')
        obj2.on()
        obj2.set_output(voltage = 0.)
        jsc = obj2.read_values()[1]

        # measurement parameters
        v_min = 0.
        v_max = voc

        # measure
        JV = np.zeros((0,2))
        for v in np.arange(0, voc, v_step):
            obj2.set_output(voltage = v)
            time.sleep(hold_time)
            j = obj2.read_values()[1]
            JV = np.vstack([JV,[v,j]])
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        
        Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
        Jpmax = JV[np.where(PV == np.amax(PV)),1][1][0]
        FF = Vpmax*Jpmax*100/(voc*jsc)
        effic = Vpmax*Jpmax/powerIn
        data = np.array([voc, jsc, Vpmax*Jpmax,FF,effic])
        return data
        #return voc, jsc, Vpmax*Jpmax, FF, effic

    # Tracking
    # dfAcqParams : self.dfAcqParams
    def tracking(self, dfAcqParams):
        num_points = float(dfAcqParams(0,'Num Track Points'))
        track_time = float(dfAcqParams(0,'Track Interval'))
        v_step = float(dfAcqParams(0,'Acq Step Voltage'))
        hold_time = float(dfAcqParams(0,'Delay Before Meas'))

        data = np.zeros((num_points, 4))
        voc, jsc, mpp = self.measure_voc_jsc_mpp(v_step = v_step, hold_time = hold_time)
        st = time.time()
        data[0, :] = [0., voc, jsc, mpp]

        for n in range(1, num_points):
            time.sleep(track_time)
            voc, jsc, mpp = self.measure_voc_jsc_mpp(v_step = v_step, hold_time = hold_time)
            data[n, :] = [time.time()-st, voc, jsc, mpp]
            #np.savetxt(filename, data, delimiter=',', header='time,Voc,Jsc,MPP')

    
    # Process JV Acquisition to result page
    def JVDeviceProcess(self, JV, deviceID, dfAcqParams, timeAcq):
        self.obj.resultswind.clearPlots(False)
        self.obj.resultswind.setupResultTable()
        perfData = self.analyseJV(float(self.obj.config.conf['Instruments']['powerIn1Sun']),JV)
        perfData = np.hstack((timeAcq, perfData))
        perfData = np.hstack((self.getDateTimeNow()[1], perfData))
        perfData = np.hstack((self.getDateTimeNow()[0], perfData))
        self.obj.resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV)
        QApplication.processEvents()
        self.obj.resultswind.show()
        QApplication.processEvents()
        time.sleep(1)
            
        self.obj.resultswind.makeInternalDataFrames(self.obj.resultswind.lastRowInd,
            self.obj.resultswind.deviceID,self.obj.resultswind.perfData,
            self.obj.resultswind.JV)

# Main Class for Acquisition
# Everything happens here!
class acqThread(QThread):

    acqJVComplete = pyqtSignal(np.ndarray, str)
    maxPowerDev = pyqtSignal(str)
    done = pyqtSignal(str)

    def __init__(self, parent_obj, numRow, numCol, dfAcqParams):
        QThread.__init__(self)
        self.dfAcqParams = dfAcqParams
        self.parent_obj = parent_obj
        self.numRow = numRow
        self.numCol = numCol

    def __del__(self):
        self.wait()

    def devAcq(self):
        # Switch to correct device and start acquisition of JV
        time.sleep(float(self.dfAcqParams.get_value(0,'Delay Before Meas')))
        JV = self.parent_obj.measure_JV(self.parent_obj.source_meter, self.dfAcqParams)
        return JV

    def run(self):
        # Activate stage
        msg = "Activating stage..."
        self.parent_obj.printMsg(msg)
        QApplication.processEvents()
        self.parent_obj.xystage = XYstage()
        if self.parent_obj.xystage.xystageInit == False:
            msg = "Stage not activated: no acquisition possible"
            self.parent_obj.printMsg(msg)
            QApplication.processEvents()
            return
        msg = "Stage activated."
        self.parent_obj.printMsg(msg)
        
        # Activate switchbox
        msg = "Activating switchbox..."
        self.parent_obj.printMsg(msg)
        QApplication.processEvents()
        try:
            self.parent_obj.switch_box = SwitchBox(self.parent_obj.obj.config.switchboxID)
        except:
            msg = "Switchbox not activated: no acquisition possible"
            self.parent_obj.printMsg(msg)
            QApplication.processEvents()
            return
        msg = "Switchbox activated."
        self.parent_obj.printMsg(msg)

        # Activate sourcemeter
        msg = "Activating sourcemeter..."
        self.parent_obj.printMsg(msg)
        QApplication.processEvents()
        try:
            self.parent_obj.source_meter = SourceMeter(self.parent_obj.obj.config.sourcemeterID)
            self.parent_obj.source_meter.set_limit(voltage=20., current=1.)
            self.parent_obj.source_meter.on()
        except:
            msg = "Sourcemeter not activated: no acquisition possible"
            self.parent_obj.parent_obj.printMsg(msg)
            QApplication.processEvents()
            return
        msg = "Sourcemeter activated."
        self.parent_obj.printMsg(msg)

        ### Setup interface and get parameters before acquisition
        self.parent_obj.obj.resultswind.clearPlots(True)
        self.parent_obj.obj.resultswind.setupDataFrame()
        operator = self.parent_obj.obj.samplewind.operatorText.text()
        msg = "Operator: " + operator
        self.parent_obj.printMsg(msg)
        msg = "Acquisition started: "+self.parent_obj.getDateTimeNow()[0]+"_"+self.parent_obj.getDateTimeNow()[1]
        self.parent_obj.printMsg(msg)
        
        # If all is OK, start acquiring
        # Start from moving to the correct substrate
        for j in range(self.numCol):
            for i in range(self.numRow):
                # convert to correct substrate number in holder
                substrateNum = self.parent_obj.getSubstrateNumber(i,j)
                substrateID = self.parent_obj.obj.samplewind.tableWidget.item(i,j).text()
                
                # Check if the holder has a substrate in that slot
                if self.parent_obj.obj.samplewind.tableWidget.item(i,j).text() != "":
                    # Move stage to desired substrate
                    if self.parent_obj.xystage.xystageInit is True:
                        msg = "Moving stage to substrate: ("+str(i+1)+", "+str(j+1)+")"
                        self.parent_obj.printMsg(msg)
                        self.parent_obj.xystage.move_to_substrate_4x4(substrateNum)
                        time.sleep(0.1)
                    else:
                        print("Skipping acquisition: stage not activated.")
                        break
                    self.max_power = []
                    self.devMaxPower = 0
                    for dev_id in range(1,7):
                        msg = " Moving to device: " + str(dev_id)+", substrate: ("+str(i+1)+", "+str(j+1)+")" 
                        self.parent_obj.printMsg(msg)
                        deviceID = substrateID+str(dev_id)
                        # prepare parameters, plots, tables for acquisition
                        msg = "  Acquiring JV from device: " + deviceID
                        self.parent_obj.printMsg(msg)

                        # Switch to correct device and start acquisition of JV
                        self.parent_obj.xystage.move_to_device_3x2(self.parent_obj.getSubstrateNumber(i, j), dev_id)
                        self.parent_obj.switch_device(i, j, dev_id)
                        JV = self.devAcq()
                    
                        #Right now the voc, jsc and mpp are extracted from the JV in JVDeviceProcess
                        self.acqJVComplete.emit(JV, deviceID)
                        self.max_power.append(np.max(JV[:, 0] * JV[:, 1]))
                        self.done.emit('  Device '+deviceID+' acquisition: complete')
                        self.devMaxPower =  np.argmax(self.max_power) + 1

                    self.maxPowerDev.emit("Main: Device with max power: "+str(self.devMaxPower))
                    self.parent_obj.obj.samplewind.colorCellAcq(i,j,"green")

        msg = "Acquisition Completed: "+ self.parent_obj.getDateTimeNow()[0]+"_"+self.parent_obj.getDateTimeNow()[1]
        self.parent_obj.obj.acquisitionwind.enableAcqPanel(True)
        self.parent_obj.obj.samplewind.enableSamplePanel(True)
        self.parent_obj.obj.enableButtonsAcq(True)
        self.parent_obj.printMsg(msg)

        # park the stage close to origin, deactivate.
        msg = "Moving the stage to substrate 6 - (2, 1)"
        self.parent_obj.printMsg(msg)
        self.parent_obj.xystage.move_to_substrate_4x4(6)
        msg = "Deactivating Stage..."
        self.parent_obj.printMsg(msg)
        self.parent_obj.xystage.end_stage_control()
        del self.parent_obj.xystage
        msg = "Stage deactivated"
        self.parent_obj.printMsg(msg)
        self.parent_obj.source_meter.off()
        del self.parent_obj.source_meter
        msg = "Sourcemeter deactivated"
        self.parent_obj.printMsg(msg)
        del self.parent_obj.switch_box
        msg = "Switchbox deactivated"
        self.parent_obj.printMsg(msg)
        
        # Re-enable panels and buttons
        self.parent_obj.obj.acquisitionwind.enableAcqPanel(True)
        self.parent_obj.obj.samplewind.resetCellAcq()
        self.parent_obj.obj.samplewind.enableSamplePanel(True)
        self.parent_obj.obj.enableButtonsAcq(True)
        QApplication.processEvents()
        msg = "System Ready"
        self.parent_obj.printMsg(msg)

                



