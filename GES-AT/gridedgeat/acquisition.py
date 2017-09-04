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
        # Activate stage
        msg = "Activating stage..."
        self.showMsg(obj, msg)
        QApplication.processEvents()
        self.xystage = XYstage()
        if self.xystage.xystageInit == False:
            msg = "Stage not activated: no acquisition possible"
            self.showMsg(obj, msg)
            QApplication.processEvents()
            return
        msg = "Stage activated."
        self.showMsg(obj, msg)
        
        # Activate switchbox
        msg = "Activating switchbox..."
        self.showMsg(obj, msg)
        QApplication.processEvents()
        try:
            self.switch_box = SwitchBox(obj.config.switchboxID)
        except:
            msg = "Switchbox not activated: no acquisition possible"
            self.showMsg(obj, msg)
            QApplication.processEvents()
            return
        msg = "Switchbox activated."
        self.showMsg(obj, msg)

        # Activate sourcemeter
        msg = "Activating sourcemeter..."
        self.showMsg(obj, msg)
        QApplication.processEvents()
        try:
            self.source_meter = SourceMeter(obj.config.sourcemeterID)
            self.source_meter.set_limit(voltage=20., current=1.)
            self.source_meter.on()
        except:
            msg = "Sourcemeter not activated: no acquisition possible"
            self.showMsg(obj, msg)
            QApplication.processEvents()
            return
        msg = "Sourcemeter activated."
        self.showMsg(obj, msg)

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
        operator = obj.samplewind.operatorText.text()
        msg = "Operator: " + operator
        self.showMsg(obj, msg)
        msg = "Acquisition started: "+self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]
        self.showMsg(obj, msg)
        
        # If all is OK, start acquiring
        for j in range(self.numCol):
            for i in range(self.numRow):
                obj.samplewind.colorCellAcq(row,column,"red")
                # convert to correct substrate number in holder
                substrateNum = obj.stagewind.getSubstrateNumber(i,j)
                
                if obj.samplewind.tableWidget.item(i,j).text() != "":
                    # Move stage to desired substrate
                    if self.xystage.xystageInit is True:
                        msg = "Moving stage to substrate("+str(i)+", "+str(j)+")"
                        self.showMsg(obj, msg)
                        self.xystage.move_to_substrate_4x4(substrateNum)
                        time.sleep(0.1)
                    else:
                        break
                    
                maxPowDeviceNum = JVAcqDevice(self, row, column, obj, deviceID, dfAcqParams)
                
                print("Device with max power: ",maxPowDeviceNum)
                obj.samplewind.colorCellAcq(row,column,"green")

        msg = "Acquisition Completed: "+ self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]
        obj.acquisitionwind.enableAcqPanel(True)
        obj.samplewind.enableSamplePanel(True)
        obj.enableButtonsAcq(True)
        self.showMsg(obj, msg)

        #if self.xystage.xystageInit is True:
        
        msg = "Moving the stage to substrate 6 - (2, 1)"
        self.showMsg(obj, msg)
        QApplication.processEvents()
        self.xystage.move_to_substrate_4x4(6)
        msg = "Deactivating Stage..."
        self.showMsg(obj,msg)
        QApplication.processEvents()
        self.xystage.end_stage_control()
        del self.xystage
        msg = "Stage deactivated"
        self.showMsg(obj,msg)
        self.source_meter.off()
        del self.source_meter
        msg = "Sourcemeter deactivated"
        self.showMsg(obj,msg)
        del self.switch_box
        msg = "Switchbox deactivated"
        self.showMsg(obj,msg)

    # Action for stop button
    def stop(self, obj):
        msg = "Acquisition stopped: " + self.getDateTimeNow()[0]+"_"+self.getDateTimeNow()[1]
        obj.stopAcqFlag = True
        self.showMsg(obj, msg)
    
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

    # Show message on status bar, terminal and log
    def showMsg(self, obj, msg):
        obj.statusBar().showMessage(msg, 5000)
        print(msg)
        logger.info(msg)
    
    # Convert coordinates as in the Sample Windown Table into the
    # correct substrate number as defined in xystage.py
    def getSubstrateNumber(self, i,j):
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
        return int((4-i)*4-(3-j)), xy_dev_id-1

    def switch_device(self, i,j, dev_id):
        "Switch operation devices"
        #self.xy_stage.move_to_device_3x2(sub_id, dev_id)
        self.switch_box.connect(*get_pcb_id(i,j, dev_id))
    
    ## measurements: JV
    # obj: self.source_meter
    # dfAcqParams : self.dfAcqParams
    def measure_JV(self, obj, dfAcqParams, filename):
        #self.source_meter.set_mode('VOLT')
        obj.set_mode('VOLT')
        obj.on()

        # measurement parameters
        v_min = float(dfAcqParams(0,'Acq Min Voltage'))
        v_max = float(dfAcqParams(0,'Acq Max Voltage'))
        v_start = float(dfAcqParams(0,'Acq Start Voltage'))
        v_step = float(dfAcqParams(0,'Acq Step Voltage'))
        scans = float(dfAcqParams(0,'Acq Num Aver Scans'))
        hold_time = float(dfAcqParams(0,'Delay Before Meas'))

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
                obj.set_output(voltage = v_list[i])
                time.sleep(hold_time)
                data[i, 2] += 1.
                data[i, 1] = (obj.read_values()[1] + data[i,1]*(data[i,2]-1)) / data[i,2]
                np.savetxt(filename, data[:, 0:2], delimiter=',', header='V,J')

        return data[:, 0:2]

    ## measurements: voc, jsp, mpp
    # obj: self.source_meter
    def measure_voc_jsc_mpp(self, obj, v_step, hold_time, powerIn):
        # voc
        obj.set_mode('CURR')
        obj.on()
        obj.set_output(current = 0.)
        voc = obj.read_values()[0]

        # jsc
        obj.set_mode('VOLT')
        obj.on()
        obj.set_output(voltage = 0.)
        jsc = obj.read_values()[1]

        # measurement parameters
        v_min = 0.
        v_max = voc

        # measure
        JV = np.zeros((0,2))
        for v in np.arange(0, voc, v_step):
            obj.set_output(voltage = v)
            time.sleep(hold_time)
            j = obj.read_values()[1]
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
    def tracking(self, dfAcqParams, filename):
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
            np.savetxt(filename, data, delimiter=',', header='time,Voc,Jsc,MPP')

    # Perform JV Acquisition over the 6 devices
    def JVAcqDevice(self, row, column, obj, deviceID, dfAcqParams):
        self.max_power = []
        for dev_id in range(1,7):
            if obj.stopAcqFlag is True:
                break
            msg = "Moving to device: "+str(dev_id)
            self.showMsg(obj, msg)
            
            self.xystage.move_to_device_3x2(self, substrateNum, dev_id)
                    
            # prepare parameters, plots, tables for acquisition
            deviceID = obj.samplewind.tableWidget.item(i,j).text()+str(dev_id)
            msg = "Acquiring JV from: " + deviceID + " - substrate("+str(row)+", "+str(column)+")"
            self.showMsg(obj, msg)
            obj.resultswind.clearPlots(False)
            obj.resultswind.setupResultTable()
            
            ### Acquisition loop should land here ##################
            self.switch_device(get_substrate_id(row, column), dev_id)
            time.sleep(acq_params['acqDelBeforeMeas'])

            JV = self.measure_JV(
                filename = deviceID+str(dev_id) + '.csv',
                acq_params = acq_params,)

            self.max_power.append(np.max(JV[:, 0] * JV[:, 1]))
            self.JVDeviceProcess(obj, JV, deviceID, dfAcqParams, 1)
        return np.argmax(max_power) + 1
    
    
    # Process JV Acquisition to result page
    def JVDeviceProcess(self, obj, JV, deviceID, dfAcqParams, timeAcq):
        perfData = self.analyseJV(float(obj.config.conf['Instruments']['powerIn1Sun']),JV)
        perfData = np.hstack((timeAcq, perfData))
        perfData = np.hstack((self.getDateTimeNow()[1], perfData))
        perfData = np.hstack((self.getDateTimeNow()[0], perfData))
        
        obj.resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV)
            
        QApplication.processEvents()
        obj.resultswind.show()
        QApplication.processEvents()
        time.sleep(1)
            
        obj.resultswind.makeInternalDataFrames(obj.resultswind.lastRowInd,
            obj.resultswind.deviceID,obj.resultswind.perfData,
            obj.resultswind.JV)

    
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

    def fakeAcq(self, row, column, obj, deviceID, dfAcqParams):
        timeAcq = 0
        # Add device number to substrate
        # this is totally to fake the cquisition of a particular device in a batch
        #new_deviceID = deviceID+str(random.randrange(1,7,1)) # Use this for completely random device number
        #new_deviceID = deviceID+"4"  # Use this temporarily for pushing data through DM via POST
        
        for i in range(self.dfAcqParams.get_value(0,'Num Track Points')):
            if obj.stopAcqFlag is True:
                break
            msg = "Scan #"+str(i+1)
            print(msg)
            logger.info(msg)
            try:
                JV = self.generateRandomJV()
            except:
                msg = "Check your acquisition settings (Start Voltage)"
                print(msg)
                logger.info(msg)
                break
            perfData = self.analyseJV(float(obj.config.conf['Instruments']['powerIn1Sun']),JV)
            perfData = np.hstack((timeAcq, perfData))
            perfData = np.hstack((self.getDateTimeNow()[1], perfData))
            perfData = np.hstack((self.getDateTimeNow()[0], perfData))
            
            obj.resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV)
            
            QApplication.processEvents()
            obj.resultswind.show()
            QApplication.processEvents()
            timeAcq = timeAcq + 1
            time.sleep(1)

    ############  Temporary section ENDS here ###########################



