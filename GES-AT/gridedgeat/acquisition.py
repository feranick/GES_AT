'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Tony Wu <tonyw@mit.edu>

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
from PyQt5.QtCore import (Qt,QObject, QThread, pyqtSlot, pyqtSignal)
from .acquisitionWindow import *
from .modules.xystage.xystage import *
from .modules.sourcemeter.sourcemeter import *
from .modules.switchbox.switchbox import *

class Acquisition(QObject):
    def __init__(self, parent=None):
        super(Acquisition, self).__init__(parent)
        
    # Collect acquisition parameters into a DataFrame to be used for storing (as csv or json)
    def getAcqParameters(self):
        self.numRow = self.parent().config.numSubsHolderRow
        self.numCol = self.parent().config.numSubsHolderCol
        pdframe = pd.DataFrame({'Operator': [self.parent().samplewind.operatorText.text()],
                'Acq Soak Voltage': [self.parent().acquisitionwind.soakVText.text()],
                'Acq Soak Time': [self.parent().acquisitionwind.soakTText.text()],
                'Acq Hold Time': [self.parent().acquisitionwind.holdTText.text()],
                'Acq Step Voltage': [self.parent().acquisitionwind.stepVText.text()],
                'Direction': [int(self.parent().acquisitionwind.directionCBox.currentIndex())],
                'Acq Rev Voltage': [int(self.parent().acquisitionwind.reverseVText.text())],
                'Acq Forw Voltage': [self.parent().acquisitionwind.forwardVText.text()],
                'Architecture': [int(self.parent().acquisitionwind.architectureCBox.currentIndex())],
                'Delay Before Meas': [self.parent().acquisitionwind.delayBeforeMeasText.text()],
                'Num Track Devices': [int(self.parent().acquisitionwind.numDevTrackText.value())],
                'Track Time': [self.parent().acquisitionwind.forwardVText.text()],
                'Comments': [self.parent().samplewind.commentsText.text()]})

        return pdframe[['Acq Soak Voltage','Acq Soak Time','Acq Hold Time',
                'Acq Step Voltage','Acq Rev Voltage','Acq Forw Voltage','Architecture',
                'Direction','Num Track Devices','Delay Before Meas','Track Time',
                'Operator','Comments']]
                
    def start(self):
        # Using ALT with Start Acquisition button:
        # 1. overrides the config settings.
        # 2. Data is saved locally
        self.modifiers = QApplication.keyboardModifiers()
        self.dfAcqParams = self.getAcqParameters()
        if self.parent().samplewind.checkTableEmpty(self.numRow, self.numCol):
            print("Please add substrates in the substrate table")
            return
        self.parent().acquisitionwind.enableAcqPanel(False)
        self.parent().samplewind.resetCellAcq()
        self.parent().samplewind.enableSamplePanel(False)
        self.parent().enableButtonsAcq(False)
        self.parent().resultswind.show()
        
        self.acq_thread = acqThread(self.numRow, self.numCol, self.dfAcqParams, self)
        self.acq_thread.Msg.connect(self.printMsg)
        self.acq_thread.acqJVComplete.connect(lambda JV,perfData,deviceID,i,j: \
                self.JVDeviceProcess(JV,perfData,deviceID,self.dfAcqParams,i,j))
        self.acq_thread.tempTracking.connect(lambda JV,perfData,deviceID,setupTable,saveData: \
                self.plotTempTracking(JV,perfData,deviceID,self.dfAcqParams,setupTable,saveData))
        self.acq_thread.colorCell.connect(lambda i,j,color: self.parent().samplewind.colorCellAcq(i,j,color))
        self.acq_thread.maxPowerDev.connect(self.printMsg)
        self.acq_thread.start()

    # Action for stop button
    def stop(self):
        quit_msg = "Are you sure you want to stop the acquisition?"
        print(quit_msg)
        reply = QMessageBox.question(self.parent(), 'Message',
                     quit_msg, QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            msg = "Acquisition stopped: " + self.acq_thread.getDateTimeNow()[0]+ \
                  " at "+self.acq_thread.getDateTimeNow()[1]
            self.acq_thread.stop()
            self.printMsg(msg)
        else:
            pass

    # Show message on log and terminal
    def printMsg(self, msg):
        print(msg)
        logger.info(msg)
        #self.parent().statusBar().showMessage(msg, 5000)
        #self.parent().statusBar.showMessage(msg, 5000)
        self.parent().statusBarLabel.setText(msg)

    # Process JV Acquisition to result page
    def JVDeviceProcess(self, JV, perfData, deviceID, dfAcqParams, i,j):
        print(perfData)
        self.parent().resultswind.clearPlots(False)
        self.parent().resultswind.setupResultTable()
        #perfData = self.analyseJV(JV)
        self.parent().resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV, True)
        QApplication.processEvents()
        time.sleep(1)
            
    # Plot temporary data from tracking
    def plotTempTracking(self, JV, perfData, deviceID, dfAcqParams, setupTable, saveData):
        self.parent().resultswind.clearPlots(False)
        if setupTable is True:
            self.parent().resultswind.setupResultTable()
        self.parent().resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV, saveData)
        QApplication.processEvents()
        time.sleep(1)

# Main Class for Acquisition
# Everything happens here!
class acqThread(QThread):

    acqJVComplete = pyqtSignal(np.ndarray, np.ndarray, str, int, int)
    tempTracking = pyqtSignal(np.ndarray, np.ndarray, str, bool, bool)
    maxPowerDev = pyqtSignal(str)
    colorCell = pyqtSignal(int,int,str)
    Msg = pyqtSignal(str)

    def __init__(self, numRow, numCol, dfAcqParams, parent=None):
        super(acqThread, self).__init__(parent)
        #QThread.__init__(self)
        self.dfAcqParams = dfAcqParams
        self.numRow = numRow
        self.numCol = numCol
        self.powerIn = float(self.parent().parent().config.conf['Instruments']['irradiance1Sun']) * \
            float(self.parent().parent().samplewind.sizeSubsCBox.currentText()) * 0.00064516
        self.tracking_points = 2

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()
        self.endAcq()
    
    '''
    # JV Acquisition
    def devAcqJV(self):
        # Switch to correct device and start acquisition of JV
        time.sleep(float(self.dfAcqParams.get_value(0,'Delay Before Meas')))
        return self.measure_JV(self.dfAcqParams)
        '''
    '''
    # Parameters (Voc, Jsc, MPP, FF, eff)
    def devAcqParams(self):
        perfData, _, _ = self.measure_voc_jsc_mpp(self.dfAcqParams)
        # Add fictious "zero" time for consistency in DataFrame for device.
        perfData = np.hstack((0., perfData))
        perfData = np.hstack((self.getDateTimeNow()[1], perfData))
        perfData = np.hstack((self.getDateTimeNow()[0], perfData))
        return np.array([perfData])
    '''
    
    def run(self):
        '''
        # Activate stage
        self.Msg.emit("Activating stage...")
        self.parent().xystage = XYstage()
        if self.parent().xystage.xystageInit == False:
            self.Msg.emit(" Stage not activated: no acquisition possible")
            self.stop()
            return
        self.Msg.emit(" Stage activated.")
        '''
        
        # Activate switchbox
        self.Msg.emit("Activating switchbox...")        
        try:
            self.parent().switch_box = SwitchBox(self.parent().parent().config.switchboxID)
        except:
            self.Msg.emit(" Switchbox not activated: no acquisition possible")
            self.stop()
            return
        self.Msg.emit(" Switchbox activated.")

        # Activate sourcemeter
        self.Msg.emit("Activating sourcemeter...")
        QApplication.processEvents()
        try:
            self.parent().source_meter = SourceMeter(self.parent().parent().config.sourcemeterID)
            self.parent().source_meter.set_limit(voltage=20., current=1.)
            self.parent().source_meter.on()
        except:
            self.Msg.emit(" Sourcemeter not activated: no acquisition possible")
            self.stop()
            return
        self.Msg.emit(" Sourcemeter activated.")

        ### Setup interface and get parameters before acquisition
        self.parent().parent().resultswind.clearPlots(True)
        self.parent().parent().resultswind.setupDataFrame()
        operator = self.parent().parent().samplewind.operatorText.text()
        self.Msg.emit("Operator: " + operator)
        self.Msg.emit("Acquisition started: "+self.getDateTimeNow()[0]+" at " + \
                self.getDateTimeNow()[1])
                
        # If all is OK, start acquiring
        # Start from moving to the correct substrate
        for j in range(self.numCol):
            for i in range(self.numRow):
                # convert to correct substrate number in holder
                substrateNum = self.getSubstrateNumber(i,j)
                substrateID = self.parent().parent().samplewind.tableWidget.item(i,j).text()
                
                # Check if the holder has a substrate in that slot
                if self.parent().parent().samplewind.tableWidget.item(i,j).text() != ""  and \
                        self.parent().parent().samplewind.activeSubs[i,j] == True:
                    self.colorCell.emit(i,j,"yellow")
                    '''
                    # Move stage to desired substrate
                    if self.parent().xystage.xystageInit is True:
                        self.Msg.emit("Moving stage to substrate #"+ \
                                        str(self.getSubstrateNumber(i,j))+ \
                                        ": ("+str(i+1)+", "+str(j+1)+")")
                        self.parent().xystage.move_to_substrate_4x4(substrateNum)
                        time.sleep(0.1)
                    else:
                        print("Skipping acquisition: stage not activated.")
                        break
                    '''
                    id_mpp_v = np.zeros((0,3))
                    #self.devMaxPower = 0
                    for dev_id in range(1,7):
                        self.Msg.emit(" Moving to device: " + str(dev_id)+", substrate #"+ \
                                str(self.getSubstrateNumber(i,j)) + \
                                ": ("+str(i+1)+", "+str(j+1)+")") 
                        deviceID = substrateID+str(dev_id)
                        # prepare parameters, plots, tables for acquisition
                        self.Msg.emit("  Acquiring JV from device: " + deviceID)
                        '''
                        # Switch to correct device and start acquisition of JV
                        self.parent().xystage.move_to_device_3x2(self.getSubstrateNumber(i, j),
                                                                   dev_id)
                        '''
                        self.switch_device(i, j, dev_id)
                        
                        # light JV
                        # self.solar_sim.shutter('ON')
                        time.sleep(float(self.dfAcqParams.get_value(0,'Delay Before Meas')))
                        
                        JV_r, JV_f = self.measure_JV(self.dfAcqParams)

                        # Acquire parameters
                        perfData = self.analyseJV(JV_r)
                        perfData_f = self.analyseJV(JV_f)
                        perfData = np.vstack((perfData_f, perfData))
                        
                        self.acqJVComplete.emit(np.hstack((JV_r, JV_f)), perfData, deviceID, i, j)
                        
                        JV = np.vstack((JV_r, JV_f))
                        
                        max_i = np.argmax(JV[:, 0] * JV[:, 1])
                        id_mpp_v = np.vstack(([dev_id, JV[max_i, 0]*JV[max_i, 1],JV[max_i, 0]],id_mpp_v))
                        self.Msg.emit('  Device '+deviceID+' acquisition: complete')

                    id_mpp_v = id_mpp_v[np.argsort(id_mpp_v[:, 1]), :]
                    id_mpp_v[:,0] = id_mpp_v[:,0].astype('int')
                    self.maxPowerDev.emit(" Device with max power: "+str(id_mpp_v[0,0]))

                    # Tracking
                    time.sleep(1)
                    tracking_points = int(self.dfAcqParams.get_value(0,'Num Track Devices'))
                    # Switch to device with max power and start tracking
                    for dev_id_f, mpp, v_mpp in id_mpp_v[:tracking_points, :]:
                        dev_id = int(dev_id_f)
                        '''
                        self.parent().xystage.move_to_device_3x2(self.getSubstrateNumber(i, j), dev_id)
                        '''
                        self.switch_device(i, j, dev_id)
                        time.sleep(float(self.dfAcqParams.get_value(0,'Delay Before Meas')))
                        
                        # Acquire dark JV
                        # self.solar_sim.shutter('OFF')
                        dark_JV_r, dark_JV_f = self.measure_JV(self.dfAcqParams)
                        perfDataDark = self.analyseDarkJV(dark_JV_r)
                        perfDataDark_f = self.analyseDarkJV(dark_JV_f)
                        perfDataDark = np.vstack((perfDataDark_f, perfDataDark))

                        self.acqJVComplete.emit(np.hstack((dark_JV_r, dark_JV_f)), perfDataDark, deviceID, i, j)
                        
                        # tracking
                        # self.solar_sim.shutter('ON')
                        perfData, JV = self.tracking(substrateID+str(dev_id),
                                                 self.dfAcqParams, v_mpp)

                        #self.acqJVComplete.emit(JV, perfData, substrateID+str(dev_id), i, j)
                        self.Msg.emit(' Device '+substrateID+str(dev_id)+' tracking: complete')
                        
                    self.colorCell.emit(i,j,"green")

        self.Msg.emit("Acquisition Completed: "+ self.getDateTimeNow()[0] + \
                " at "+self.getDateTimeNow()[1])
        self.endAcq()

    def endAcq(self):
        self.parent().parent().acquisitionwind.enableAcqPanel(True)
        self.parent().parent().samplewind.enableSamplePanel(True)
        self.parent().parent().enableButtonsAcq(True)

        # park the stage close to origin, deactivate.
        try:
            '''
            self.Msg.emit(" Moving stage to parking position")
            self.parent().xystage.move_abs(5,5)
            self.Msg.emit("Deactivating Stage...")
            self.parent().xystage.end_stage_control()    
            del self.parent().xystage
            self.Msg.emit("Stage deactivated")
            '''
            self.parent().source_meter.off()
            del self.parent().source_meter
            self.Msg.emit("Sourcemeter deactivated")
            del self.parent().switch_box
            self.Msg.emit("Switchbox deactivated")
        except:
            pass     
        
        # Re-enable panels and buttons
        self.parent().parent().acquisitionwind.enableAcqPanel(True)
        self.parent().parent().samplewind.enableSamplePanel(True)
        self.parent().parent().enableButtonsAcq(True)
        QApplication.processEvents()
        self.Msg.emit("System: ready")

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
        self.parent().switch_box.connect(*self.get_pcb_id(i,j, dev_id))
    
    ## measurements: JV - new flow
    # dfAcqParams : self.dfAcqParams
    
    def measure_JV(self, dfAcqParams):
        #self.source_meter.set_mode('VOLT')
        self.parent().source_meter.set_mode('VOLT')
        self.parent().source_meter.on()

        # measurement parameters
        v_soak = float(dfAcqParams.get_value(0,'Acq Soak Voltage'))
        soak_time = float(dfAcqParams.get_value(0,'Acq Soak Time'))
        hold_time = float(dfAcqParams.get_value(0,'Acq Hold Time'))
        v_step = float(dfAcqParams.get_value(0,'Acq Step Voltage'))
        v_r = int(dfAcqParams.get_value(0,'Acq Rev Voltage'))
        v_f = float(dfAcqParams.get_value(0,'Acq Forw Voltage'))

        direction = int(dfAcqParams.get_value(0,'Direction'))
        
        if int(dfAcqParams.get_value(0,'Architecture')) == 0:
            polarity = 1
        else:
            polarity = -1
        #polarity = 1 if acq_params['acqPolarity'] == 'pn' else -1

        # enforce
        #if v_r < 0 and v_f > 0:
        #    raise ValueError('Voltage Errors')

        # create list of voltage to measure
        if direction == 0:
            v_list = list(np.arange(v_r-1e-9, v_f+1e-9, v_step))
        else:
            v_list = list(np.arange(v_f+1e-9, v_r-1e-9, -v_step))

        self.parent().source_meter.set_output(voltage = polarity*v_soak)
        time.sleep(soak_time)

        # measure
        def __sweep(v_list, hold_time):
            data = np.zeros((len(v_list), 2))
            data[:, 0] = v_list
            for i in range(len(v_list)):
                v = v_list[i]
                self.parent().source_meter.set_output(voltage = polarity*v)
                time.sleep(hold_time)
                data[i, 1] = polarity*self.parent().source_meter.read_values()[1]
            return data
        
        JV_r = __sweep(v_list, hold_time)
        JV_f = __sweep(v_list[::-1], hold_time)
        return JV_r, JV_f

    
    ## measurements: voc, jsc
    def measure_voc_jsc(self):
        # voc
        self.parent().source_meter.set_mode('CURR')
        self.parent().source_meter.on()
        self.parent().source_meter.set_output(current = 0.)
        voc = self.parent().source_meter.read_values()[0]

        # jsc
        self.parent().source_meter.set_mode('VOLT')
        self.parent().source_meter.on()
        self.parent().source_meter.set_output(voltage = 0.)
        jsc = self.parent().source_meter.read_values()[1]
        return voc, jsc

    ## measurements: voc, jsc, mpp
    def measure_voc_jsc_mpp(self, dfAcqParams):
        v_step = float(dfAcqParams.get_value(0,'Acq Step Voltage'))
        hold_time = float(dfAcqParams.get_value(0,'Delay Before Meas'))

        # measurements: voc, jsc
        voc, jsc = self.measure_voc_jsc()

        # measurement parameters
        v_min = 0.
        v_max = voc

        # measure
        JV = np.zeros((0,2))
        for v in np.arange(0, voc, v_step):
            self.parent().source_meter.set_output(voltage = v)
            time.sleep(hold_time)
            j = self.parent().source_meter.read_values()[1]
            JV = np.vstack([JV,[v,j]])
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]

        try:
            Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
            Jpmax = JV[np.where(PV == np.amax(PV)),1][0][0]
            FF = Vpmax*Jpmax*100/(voc*jsc)
            effic = Vpmax*Jpmax/self.powerIn
        except:
            Vpmax = 0.
            Jpmax = 0.
            FF = 0.
            effic = 0.
        data = np.array([voc, jsc, Vpmax*Jpmax,FF,effic])
        return data, Vpmax, JV

    ## New Flow
    # Tracking (take JV once and track Vpmax)
    # dfAcqParams : self.dfAcqParams
    def tracking(self, deviceID, dfAcqParams, v_mpp):
        #hold_time = float(dfAcqParams.get_value(0,'Delay Before Meas'))
        #numPoints = int(dfAcqParams.get_value(0,'Num Track Points'))
        track_time = float(dfAcqParams.get_value(0,'Track Time'))
        hold_time = float(dfAcqParams.get_value(0,'Acq Hold Time'))

        dv = 0.0001
        step_size = 0.1
        if int(dfAcqParams.get_value(0,'Architecture')) == 0:
            polarity = 1
        else:
            polarity = -1
        
        def __measure_power(v):
            self.parent().source_meter.set_output(voltage = polarity*v)
            time.sleep(hold_time)
            return -1 * v * self.parent().source_meter.read_values()[0]
        
        perfData = np.zeros((0,10))
        JV = np.zeros([1,4])
        data = np.array([0,0, v_mpp, __measure_power(v_mpp), 0,0,True])
        data = np.hstack(([self.getDateTimeNow()[0],self.getDateTimeNow()[1],0], data))
        perfData = np.vstack((data, perfData))
        self.tempTracking.emit(JV, perfData, deviceID, True, False)
        
        v = v_mpp
        start_time = time.time()
        self.Msg.emit("Tracking device: "+deviceID+"...")

        while time.time() - start_time <= track_time:
            mp = __measure_power(v)
            data = np.array([ 0, 0, v, mp , 0, 0, True])
            data = np.hstack(([self.getDateTimeNow()[0],
                                   self.getDateTimeNow()[1],time.time() - start_time], data))
            print(data)
            print(data.shape)

            perfData = np.vstack((data, perfData))
            print(perfData.shape)
            self.tempTracking.emit(JV, perfData, deviceID, False, False)
            # calculate gradient
            mpd = __measure_power(v + dv)
            grad_mp = (mpd-mp)/dv
            v += grad_mp * step_size
        self.tempTracking.emit(JV, perfData, deviceID, False, True)
        return perfData

    # Extract parameters from JV
    def analyseJV(self, JV):
        powerIn = float(self.parent().parent().config.conf['Instruments']['irradiance1Sun'])*0.00064516
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        # measurements: voc, jsc
        Voc, Jsc = self.measure_voc_jsc()
        #Voc = JV[JV.shape[0]-1,0]
        #Jsc = JV[0,1]
        Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
        Jpmax = JV[np.where(PV == np.amax(PV)),1][0][0]
        if Voc != 0. and Jsc != 0.:
            FF = Vpmax*Jpmax*100/(Voc*Jsc)
            effic = Vpmax*Jpmax/self.powerIn
        else:
            FF = 0.
            effic = 0.
        data = np.array([0, Voc, Jsc, Vpmax, Vpmax*Jpmax,FF,effic,True])
        data = np.hstack((self.getDateTimeNow()[1], data))
        data = np.hstack((self.getDateTimeNow()[0], data))
        return np.array([data])
        
    def analyseDarkJV(self, JV):
        data = np.array([0, 0, 0, 0, 0, 0, 0, False])
        data = np.hstack((self.getDateTimeNow()[1], data))
        data = np.hstack((self.getDateTimeNow()[0], data))
        return np.array([data])

    # Get date/time
    def getDateTimeNow(self):
        return str(datetime.now().strftime('%Y-%m-%d')),\
                    str(datetime.now().strftime('%H-%M-%S'))
