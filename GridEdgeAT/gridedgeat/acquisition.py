'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017-2019 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017-2019 Roberto Brenes <rbrenes@mit.edu>
Copyright (C) 2017 Tony Wu <tonyw@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import time, random, math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication,QAbstractItemView)
from PyQt5.QtCore import (Qt,QObject, QThread, pyqtSlot, pyqtSignal)
from .acquisitionWindow import *
from .modules.xystage.xystage import *
from .modules.sourcemeter.sourcemeter import *
from .modules.switchbox.switchbox import *
from .modules.shutter.shutter import *

####################################################################
# Acquisition
####################################################################
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
                'Acq Rev Voltage': [self.parent().acquisitionwind.reverseVText.text()],
                'Acq Forw Voltage': [self.parent().acquisitionwind.forwardVText.text()],
                'Architecture': [int(self.parent().acquisitionwind.architectureCBox.currentIndex())],
                'Delay Before Meas': [self.parent().acquisitionwind.delayBeforeMeasText.text()],
                'Num Track Devices': [int(self.parent().acquisitionwind.numDevTrackText.value())],
                'Track Time': [self.parent().acquisitionwind.trackTText.text()],
                'Hold Track Time': [self.parent().acquisitionwind.holdTrackTText.text()],
                'Device Area': [self.parent().samplewind.deviceAreaText.text()],
                'Comments': [self.parent().samplewind.commentsText.text()],
                'DevArchitecture': [self.parent().samplewind.deviceArchCBox.currentText()]},)

        return pdframe[['Acq Soak Voltage','Acq Soak Time','Acq Hold Time',
                'Acq Step Voltage','Acq Rev Voltage','Acq Forw Voltage','Architecture',
                'Direction','Num Track Devices','Delay Before Meas','Track Time',
                'Hold Track Time', 'Device Area', 'Operator','Comments','DevArchitecture']]
    
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
                self.JVDeviceProcess(JV,perfData,deviceID,i,j))
        self.acq_thread.tempTracking.connect(lambda JV,perfData,deviceID,setupTable,saveData: \
                self.plotTempTracking(JV,perfData,deviceID,setupTable,saveData))
        self.acq_thread.colorCell.connect(lambda i,j,color: self.parent().samplewind.colorCellAcq(i,j,color))
        self.acq_thread.maxPowerDev.connect(self.printMsg)
        self.acq_thread.start()

    # Action for stop button
    def stop(self):
        quit_msg = "Are you sure you want to stop the acquisition?"
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
        self.parent().statusBarLabel.setText(msg)

    # Process JV Acquisition to result page
    def JVDeviceProcess(self, JV, perfData, deviceID, i,j):
        self.parent().resultswind.clearPlots(False)
        self.parent().resultswind.setupResultTable()
        self.parent().resultswind.processDeviceData(deviceID, self.dfAcqParams, perfData, JV, True, False)
        QApplication.processEvents()
        time.sleep(1)
            
    # Plot temporary data from tracking
    def plotTempTracking(self, JV, perfData, deviceID, setupTable, saveData):
        if setupTable is True:
            self.parent().resultswind.setupResultTable()
        self.parent().resultswind.processDeviceData(deviceID, self.dfAcqParams, perfData, JV, saveData, True)
        QApplication.processEvents()
        if saveData is True:
            time.sleep(1)

    # Convert coordinates as in the Sample Windown Table into the
    # correct substrate number as defined in xystage.py
    def getSubstrateNumber(self, i,j):
        if i > 3 or j > 3:
            print("indexes outside boundaries, resetting to substrate 1")
            return 1
        else:
            #return int(i+4*j+1)
            #return int(j+4*(3-i)+1)
            return int(4*(4-j)-i)

####################################################################
# Independent Thread for Acquisition
# Everything happens here!
####################################################################
class acqThread(QThread):

    acqJVComplete = pyqtSignal(np.ndarray, np.ndarray, str, int, int)
    tempTracking = pyqtSignal(np.ndarray, np.ndarray, str, bool, bool)
    maxPowerDev = pyqtSignal(str)
    colorCell = pyqtSignal(int,int,str)
    Msg = pyqtSignal(str)
    shutterFlag = pyqtSignal(str)

    def __init__(self, numRow, numCol, dfAcqParams, parent=None):
        super(acqThread, self).__init__(parent)
        self.dfAcqParams = dfAcqParams
        self.numRow = numRow
        self.numCol = numCol
        self.powerIn = float(self.parent().parent().config.conf['Instruments']['irradiance1Sun'])
        self.tracking_points = 2
        self.stopAcqFlag = False

    def __del__(self):
        self.wait()

    def stop(self):
        self.stopAcqFlag = True
        print(" Stopping acquisition. Please wait...")
        while self.isRunning():
            self.wait(100)
        if hasattr(self.parent(), "shutter"):
            self.parent().shutter.closed()
        self.endAcq()
        print(" Stopping acquisition successful")
        self.terminate()
    
    def run(self):
        # Activate stage
        self.Msg.emit("Activating stage...")
        # If stage is open in stage window, close.
        if self.parent().parent().stagewind.activeStage:
            self.parent().parent().stagewind.activateStage()
        self.parent().xystage = XYstage(self.parent().parent().config.xDefStageOrigin,
                            self.parent().parent().config.yDefStageOrigin)
        if self.parent().xystage.xystageInit == False:
            self.Msg.emit(" Stage not activated: no acquisition possible")
            self.stop()
            return
        self.Msg.emit(" Stage activated.")
        
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
        
        # Activate shutter
        self.Msg.emit("Activating shutter...")
        try:
            if not hasattr(self.parent(),"shutter"):
                self.parent().shutter = Shutter()
        except:
            self.Msg.emit(" Shutter not activated: no acquisition possible")
            self.stop()
            return
        self.parent().shutter.closed()
        self.Msg.emit(" Shutter activated and closed.")

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
                if self.stopAcqFlag == True:
                    break
                # convert to correct substrate number in holder
                substrateNum = self.parent().getSubstrateNumber(i,j)
                substrateID = self.parent().parent().samplewind.tableWidget.item(i,j).text()
                
                # Check if the holder has a substrate in that slot
                if self.parent().parent().samplewind.tableWidget.item(i,j).text() != ""  and \
                        self.parent().parent().samplewind.activeSubs[i,j] == True:
                    self.colorCell.emit(i,j,"yellow")
                    self.parent().parent().samplewind.checkCreateLotDM(substrateID, i, j)
                    # Move stage to desired substrate
                    if self.parent().xystage.xystageInit is True:
                        self.Msg.emit("Moving stage to substrate #"+ \
                                        str(self.parent().getSubstrateNumber(i,j))+ \
                                        ": ("+str(4-i)+", "+str(4-j)+")")
                        self.parent().xystage.move_to_substrate_4x4(substrateNum)
                        time.sleep(0.1)
                    else:
                        print("Skipping acquisition: stage not activated.")
                        break
                    
                    id_mpp_v = np.zeros((0,7))
                    #self.devMaxPower = 0
                    for dev_id in range(1,7):
                        if self.stopAcqFlag == True:
                            break
                        self.Msg.emit(" Moving to device: " + str(dev_id)+", substrate #"+ \
                                str(self.parent().getSubstrateNumber(i,j))) 
                        deviceID = substrateID+str(dev_id)
                        # prepare parameters, plots, tables for acquisition
                        self.Msg.emit("  Acquiring JV from device: " + deviceID)
                        
                        # Switch to correct device and start acquisition of JV
                        self.parent().xystage.move_to_device_3x2(self.parent().getSubstrateNumber(i, j), dev_id)
                        self.switch_device(i, j, dev_id)
                        
                        # light JV
                        # open the shutter
                        self.parent().shutter.open()
                        time.sleep(0.2)
                        time.sleep(float(self.dfAcqParams.at[0,'Delay Before Meas']))
                        JV_r, JV_f = self.measure_JV()

                        # Acquire parameters
                        perfData = self.analyseJV(JV_r)
                        perfData_f = self.analyseJV(JV_f)
                        perfData = np.vstack((perfData_f, perfData))
                        
                        self.acqJVComplete.emit(np.hstack((JV_r, JV_f)), perfData, deviceID, i, j)
                        
                        # Prepare stack for list of best devices
                        JV = np.vstack((JV_r, JV_f))
                        PV = np.zeros(JV.shape)
                        PV[:,0] = JV[:,0]
                        PV[:,1] = JV[:,0]*JV[:,1]
                        max_i = np.argmin(PV[:,1])
                        id_mpp_v = np.vstack(([dev_id, JV[max_i, 0]*JV[max_i, 1],JV[max_i, 0],
                                    perfData[0][3], perfData[0][4], perfData[0][7],
                                    perfData[0][8]],id_mpp_v))
                        self.Msg.emit('  Device '+deviceID+' acquisition: complete')
                    if self.stopAcqFlag == True:
                            break
                    
                    id_mpp_v = id_mpp_v.astype(np.float32)
                    id_mpp_v = id_mpp_v[sorted(range(len(id_mpp_v[:,1])), key=lambda k: id_mpp_v[:,1][k])]
                    id_mpp_v[:,0] = id_mpp_v[:,0].astype('int')

                    self.maxPowerDev.emit("\n Summary of device with max power: "+str(int(id_mpp_v[0,0])))
                    self.maxPowerDev.emit("  Max power (mW/cm^2): {0:0.3e}".format(id_mpp_v[0,1]))
                    self.maxPowerDev.emit("  V at Max power (V): {0:0.3e}".format(id_mpp_v[0,2]))
                    self.maxPowerDev.emit("  Voc (V): {0:0.3e}".format(id_mpp_v[0,3]))
                    self.maxPowerDev.emit("  Jsc (mA/cm^2): {0:0.3e}".format(id_mpp_v[0,4]))
                    self.maxPowerDev.emit("  FF: {0:0.2f}".format(id_mpp_v[0,5]))
                    self.maxPowerDev.emit("  PCE[%]: {0:0.2f}\n".format(id_mpp_v[0,6]))
                    
                    # Tracking
                    time.sleep(1)
                    tracking_points = int(self.dfAcqParams.at[0,'Num Track Devices'])
                    # Switch to device with max power and start tracking
                    for dev_id, mpp, v_mpp, voc_mpp, jsc_mpp, ff_mpp, pcs_mpp in id_mpp_v[:tracking_points, :]:
                        dev_id = int(dev_id)
                        v_mpp = float(v_mpp)
                        
                        # Move and activate correct device
                        self.parent().xystage.move_to_device_3x2(self.parent().getSubstrateNumber(i, j), dev_id)
                        self.switch_device(i, j, dev_id)
                        time.sleep(float(self.dfAcqParams.at[0,'Delay Before Meas']))
                        
                        # Acquire dark JV
                        # close the shutter
                        self.parent().shutter.closed()
                        time.sleep(0.2)

                        self.Msg.emit(" Acquiring dark JV for device: "+substrateID+str(dev_id))
                        dark_JV_r, dark_JV_f = self.measure_JV()
                        perfDataDark = self.analyseDarkJV(dark_JV_r)
                        perfDataDark_f = self.analyseDarkJV(dark_JV_f)
                        perfDataDark = np.vstack((perfDataDark_f, perfDataDark))
                        self.acqJVComplete.emit(np.hstack((dark_JV_r, dark_JV_f)),
                                                perfDataDark, substrateID+str(dev_id), i, j)
                        time.sleep(1)
                        # tracking
                        # open the shutter
                        self.parent().shutter.open()
                        time.sleep(0.2)
        
                        perfData, JV = self.tracking(substrateID+str(dev_id), v_mpp)
                        self.Msg.emit(' Device '+substrateID+str(dev_id)+' tracking: complete')
                        
                    self.colorCell.emit(i,j,"green")

        # close the shutter
        self.parent().shutter.closed()
        self.Msg.emit("Acquisition Completed: "+ self.getDateTimeNow()[0] + \
                " at "+self.getDateTimeNow()[1])
        self.endAcq()

    def endAcq(self):
        self.parent().parent().acquisitionwind.enableAcqPanel(True)
        self.parent().parent().samplewind.enableSamplePanel(True)
        self.parent().parent().enableButtonsAcq(True)

        # park the stage close to origin, deactivate.
        try:
            self.parent().switch_box.open_all()
            del self.parent().switch_box
            self.Msg.emit("Switchbox deactivated")
            self.Msg.emit(" Moving stage to parking position")
            self.parent().xystage.move_abs(5,5)
            self.Msg.emit("Deactivating Stage...")
            self.parent().xystage.end_stage_control()    
            del self.parent().xystage
            self.Msg.emit("Stage deactivated")
            self.parent().source_meter.off()
            del self.parent().source_meter
            self.Msg.emit("Sourcemeter deactivated")
            del self.parent().shutter
            self.Msg.emit("Shutter deactivated")
        except:
            pass     
        
        # Re-enable panels and buttons
        self.parent().parent().acquisitionwind.enableAcqPanel(True)
        self.parent().parent().samplewind.enableSamplePanel(True)
        self.parent().parent().enableButtonsAcq(True)
        QApplication.processEvents()
        self.Msg.emit("System: ready")

    ## low level api
    # xy substrate layout (default)
    # column:  1 ==> 4     row:
    # 16 | 12 | 8 | 4     4
    # 15 | 11 | 7 | 3     3
    # 14 | 10 | 6 | 2      2
    # 13 | 9  | 5 | 1      1
    # xy device layout (default)
    # |   ----   |
    # | 1 |  | 4 |
    # | 2 |  | 5 |
    # | 3 |  | 6 |
    # |   ----   |
    
    def get_pcb_id(self, i,j, xy_dev_id):
        "ID converison between xy to pcb"
        #return int((4-i)*4-(3-j)), xy_dev_id
        return int((4-j)*4-i), xy_dev_id

    def switch_device(self, i,j, dev_id):
        "Switch operation devices"
        self.parent().switch_box.connect(*self.get_pcb_id(i,j, dev_id))
    
    ## measurements: JV - new flow
    def measure_JV(self):
        self.parent().source_meter.set_mode('VOLT')
        self.parent().source_meter.on()

        # measurement parameters
        v_soak = float(self.dfAcqParams.at[0,'Acq Soak Voltage'])
        soak_time = float(self.dfAcqParams.at[0,'Acq Soak Time'])
        hold_time = float(self.dfAcqParams.at[0,'Acq Hold Time'])
        v_step = float(self.dfAcqParams.at[0,'Acq Step Voltage'])
        v_r = float(self.dfAcqParams.at[0,'Acq Rev Voltage'])
        v_f = float(self.dfAcqParams.at[0,'Acq Forw Voltage'])
        direction = int(self.dfAcqParams.at[0,'Direction'])
        deviceArea = float(self.dfAcqParams.at[0,'Device Area'])

        if int(self.dfAcqParams.at[0,'Architecture']) == 0:
            polarity = 1
        else:
            polarity = -1

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
                data[i, 1] = polarity*self.parent().source_meter.read_values(deviceArea)[1]
            return data
        
        JV_r = __sweep(v_list, hold_time)
        JV_f = __sweep(v_list[::-1], hold_time)
        return JV_r, JV_f

    ## measurements: voc, jsc
    def measure_voc_jsc(self):
        deviceArea = float(self.dfAcqParams.at[0,'Device Area'])
        # voc
        self.parent().source_meter.set_mode('CURR')
        self.parent().source_meter.on()
        self.parent().source_meter.set_output(current = 0.)
        voc = self.parent().source_meter.read_values(deviceArea)[0]

        # jsc
        self.parent().source_meter.set_mode('VOLT')
        self.parent().source_meter.on()
        self.parent().source_meter.set_output(voltage = 0.)
        jsc = self.parent().source_meter.read_values(deviceArea)[1]
        return voc, jsc

    ## measurements: voc, jsc
    def calculate_voc_jsc(self, JV):
        try:
            jsc = interp1d(JV[:,0],JV[:,1])(0)
            voc = interp1d(JV[:,1],JV[:,0])(0)
        except:
            self.Msg.emit("Failed to calculate Voc and Jsc")
            jsc = 0.
            voc = 0.
        return voc, jsc
    
    # Tracking (take JV once and track Vpmax) - testing
    def tracking(self, deviceID, v_mpp):
        track_time = float(self.dfAcqParams.at[0,'Track Time'])
        deviceArea = float(self.dfAcqParams.at[0,'Device Area'])
        hold_time = float(self.dfAcqParams.at[0,'Acq Hold Time'])
        hold_track_time = float(self.dfAcqParams.at[0,'Hold Track Time'])
        dv = 0.001

        if int(self.dfAcqParams.at[0,'Architecture']) == 0:
            polarity = 1
        else:
            polarity = -1
        
        def __measure_power(v):
            self.parent().source_meter.set_output(voltage = polarity*v)
            return polarity* v * self.parent().source_meter.read_values(deviceArea)[1]
        
        #this is to prevent the tracking to start before the dark JV is completely processed.
        time.sleep(2)

        # light JV
        # open the shutter
        self.Msg.emit("  Acquiring JV from device: " + deviceID)
        self.parent().shutter.open()
        time.sleep(0.2)
        JVtrack_r, JVtrack_f = self.measure_JV()
       
        # Prepare stack for list of best devices
        JVtrack = np.vstack((JVtrack_r, JVtrack_f))
        PVtrack = np.zeros(JVtrack.shape)
        PVtrack[:,0] = JVtrack[:,0]
        PVtrack[:,1] = JVtrack[:,0]*JVtrack[:,1]
        max_i = np.argmin(PVtrack[:,1])

        v = PVtrack[:,0][max_i]
        mp = PVtrack[:,1][max_i]

        perfData = np.zeros((0,10))
        JV = np.zeros([1,4], dtype=float)
        data = np.array([0,0, 0, v, mp, 0,0,1])
        data = np.hstack(([self.getDateTimeNow()[0],self.getDateTimeNow()[1]], data))
        perfData = np.vstack((data, perfData))
        self.tempTracking.emit(JV, perfData, deviceID, True, False)

        self.Msg.emit(" Tracking device: "+deviceID+"...")
        start_time = time.time()

        while time.time() - start_time <= track_time:
            print(" Time step [s]: {0:0.1f}".format(time.time() - start_time))
            print("  Voltage at max power point [V]: {0:0.3e}".format(v))
            print("  Maximum power [mW]: {0:0.3e}".format(mp))
            print("  Voltage [V]: {0:0.3e}".format(v))
            print("  Polarity: {0:0.1e}".format(polarity))

            dv2neg_p =__measure_power(v-2*dv)
            dvneg_p =__measure_power(v-dv)
            mp= __measure_power(v)            
            dvpos_p =__measure_power(v+dv)
            dv2pos_p =__measure_power(v+2*dv)

            #print("DEBUG")
            #print("dvpos_p = ",dvpos_p)
            #print("dv2pos_p = ",dv2pos_p)
            #print("dvneg_p = ",dvneg_p)
            #print("dv2neg_p = ",dv2neg_p)
            #print("mp = ",mp)
            
            pow_array=np.array([dv2neg_p,dvneg_p,mp,dvpos_p,dv2pos_p])
            vpow_array=np.array([v-2*dv,v-dv,v,v+dv,v+2*dv])

            mpp_index = np.argmin(pow_array)
            v = vpow_array[mpp_index]
            mp = pow_array[mpp_index]

            # DEBUG only
            #if mpp_index==3:
            #    print('dvpos_p<mp, mp=dvpos_p',mp)
            #if mpp_index==4:
            #    print('dv2pos_p<mp, mp=dv2pos_p',mp)
            #if mpp_index==1:
            #    print('dvneg_p<mp, mp=dvneg_p',mp)
            #if mpp_index==0:
            #    print('dv2neg_p<mp, mp=dv2neg_p',mp)
            #if mpp_index==2:
            #   print("else, mp=mp",mp)
            # END DEBUG
            
            # Convention is that maximum power point is the most negative power, so we want to minimize power
            # if dvpos_p<(mp) and dvpos_p<dv2pos_p:
            #     v+=dv
            #     mp=dvpos_p
            #     print("dvpos_p<mp, mp=dvpos_p",mp)
            # elif dvneg_p<(mp):
            #     v-=dv
            #     mp=dvneg_p
            #     print("dvneg_p<mp, mp=dvneg_p",mp)
            # else:
            #     v=v
            #     mp=__measure_power(v)
            #     print("else, mp=mp",mp)

            # if dvpos_p > 0 or dvneg_p > 0:
            #     dv -=0.01
            #     print("Rescaling dv =",dv)
            # else:
            #     dp_dvpos = (dvpos_p-mp)/dv
            #     dp_dvneg = (dvneg_p-mp)/dv
            
            #     if abs(dvpos_p)>abs(mp):
            #         v+=dv
            #         mp=dvpos_p
            #         print("dvpos_p>mp, mp=dvpos_p",mp)
            #     elif abs(dvneg_p)>abs(mp):
            #         v-=dv
            #         mp=dvneg_p
            #         print("dvneg_p>mp, mp=dvneg_p",mp)
            #     else:
            #         v=v
            #         mp=mp
            #         print("else, mp=mp",mp)

            data = np.array([ 0, 0, v, mp , 0, 0, 1])
            data = np.hstack(([self.getDateTimeNow()[0],self.getDateTimeNow()[1],time.time() - start_time], data))
            perfData = np.vstack((data, perfData))
            self.tempTracking.emit(JV, perfData, deviceID, False, False)
            time.sleep(hold_track_time)
        self.tempTracking.emit(JV, perfData, deviceID, False, True)
        return perfData, JV
    
    # Extract parameters from JV
    def analyseJV(self, JV):
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        # measurements: voc, jsc
        Voc, Jsc = self.calculate_voc_jsc(JV)

        # find mpp
        ind_Pmax = np.argmin(PV[:,1])
        Jpmax = JV[ind_Pmax,1]
        Vpmax = JV[ind_Pmax,0]
        
        if Voc != 0. and Jsc != 0.:
            FF = Vpmax*Jpmax/(Voc*Jsc)
            effic = abs(100*Vpmax*Jpmax/self.powerIn)
        else:
            FF = 0.
            effic = 0.
        data = np.array([0, Voc, Jsc, Vpmax, Vpmax*Jpmax,FF,effic,1])
        data = np.hstack((self.getDateTimeNow()[1], data))
        data = np.hstack((self.getDateTimeNow()[0], data))
        return np.array([data])
        
    def analyseDarkJV(self, JV):
        data = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        data = np.hstack((self.getDateTimeNow()[1], data))
        data = np.hstack((self.getDateTimeNow()[0], data))
        return np.array([data])

    # Get date/time
    def getDateTimeNow(self):
        return str(datetime.now().strftime('%Y-%m-%d')),\
                    str(datetime.now().strftime('%H-%M-%S'))

