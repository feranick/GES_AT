'''
queryDataManagementWindow.py
-----------------------------
Classes for providing a graphical user interface
for the dataLoadDMWindow

Copyright (C) 2017-2019 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys, json, requests, webbrowser
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QAbstractItemView,
                             QLabel,QLineEdit, QTextEdit, QTableWidget,
                             QTableWidgetItem,QAction,QHeaderView,QMenu,
                             QApplication)
from PyQt5.QtCore import (QRect,pyqtSlot,pyqtSignal,Qt)
from PyQt5.QtGui import (QCursor)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .dataManagement import *
from . import logger

####################################################################
#   Window for data loading form DM
####################################################################
class DataLoadDMWindow(QMainWindow):
    deviceData = pyqtSignal(str, np.ndarray, pd.DataFrame, np.ndarray)

    def __init__(self, parent=None):
        super(DataLoadDMWindow, self).__init__(parent)
        self.title = 'Open Data from DM'
        self.deviceID = ""
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(QRect(10, 30, 360, 640))
        self.textbox = QLineEdit(self)
        self.textbox.setGeometry(QRect(15, 15, 180, 30))
        self.textbox.setToolTip("Ex: NF190203AA")
        self.textbox.setText("")
        self.button = QPushButton('Search DM', self)
        self.button.setGeometry(QRect(205, 15, 100, 30))
        
        self.resTableDMW = 340
        self.resTableDMH = 260
        self.resTableDMWidget = QTableWidget(self)
        self.resTableDMWidget.setGeometry(QRect(10, 60, self.resTableDMW, self.resTableDMH))
        self.resTableDMWidget.setToolTip("Right click for more options")
        self.resTableDMWidget.setColumnCount(3)
        self.resTableDMWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableDMWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Device"))
        self.resTableDMWidget.setHorizontalHeaderItem(2,QTableWidgetItem("Type"))
        self.resTableDMWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.resTableDMWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.textDatabox = QTextEdit(self)
        self.textDatabox.setGeometry(QRect(10, 330, 340, 300))
        self.textDatabox.setReadOnly(True)
        
        self.resTableDMWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.button.clicked.connect(self.onSearchButtonClick)
        self.resTableDMWidget.itemDoubleClicked.connect(self.onTableEntryDoubleClick)
        self.resTableDMWidget.itemClicked.connect(self.onTableEntrySingleClick)
        self.show()
    
    # Process Key Events
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.onSearchButtonClick()
    
    # Get list of devices data from DM
    @pyqtSlot()
    def onSearchButtonClick(self):
        self.deviceID = self.textbox.text()
        self.textbox.setText("")
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        #print(" Number of Measurement entries: ",db.Measurement.find({'substrate':self.deviceID}).count())
        try:
            for cursor in db.Measurement.find({'substrate':self.deviceID}):
                if cursor['name']=="JV_r" or cursor['name']=="JV_dark_r" or cursor['name']=="tracking":
                    self.resTableDMWidget.insertRow(0)
                    self.resTableDMWidget.setItem(0, 0,QTableWidgetItem(self.deviceID))
                    self.resTableDMWidget.setItem(0, 1,QTableWidgetItem(cursor['itemId']))
                    if cursor['measType'] == "JV":
                        self.resTableDMWidget.setItem(0, 2,QTableWidgetItem("JV"))
                    elif cursor['measType'] == "JV_dark":
                        self.resTableDMWidget.setItem(0, 2,QTableWidgetItem("JV_dark"))
                    elif cursor['measType'] == "tracking":
                        self.resTableDMWidget.setItem(0, 2,QTableWidgetItem("tracking"))
            try:
                self.resTableDMWidget.item(0,0).setToolTip("Double click to plot data")
            except:
                pass
        
            QApplication.processEvents()
        except:
           print(" Error in reading from DM. Aborting")
            
    #  Push DM data back to parent for plotting (double click)
    @pyqtSlot()
    def onTableEntryDoubleClick(self):
        selectedRows = list(set([ i.row() for i in self.resTableDMWidget.selectedItems()]))
        for row in selectedRows:
            substrate, device, perfData, JV, acqParams = self.getDMData(row)
            try:
                self.deviceData.emit(substrate+device, perfData, acqParams, JV)
            except:
                print(" Failed to load file from DM.")
    
    #  Show data parameters from DM (single click)
    @pyqtSlot()
    def onTableEntrySingleClick(self):
        selectedRows = list(set([ i.row() for i in self.resTableDMWidget.selectedItems()]))
        for row in selectedRows:
            substrate, device, perfData, JV, acqParams = self.getDMData(row)
            #try:
            text = "Substrate: "+substrate+"  Device: "+device+ \
                    "\nDate/Time: "+perfData[0,0]+"  "+perfData[0,1]+\
                    "\nVoc F, Voc R: {0:0.2f}  {1:0.2f}".format(float(perfData[0,3]),float(perfData[1,3]))+ \
                    "\nJsc F, Jsc R: {0:0.2f}  {1:0.2f}".format(float(perfData[0,4]),float(perfData[1,4]))+ \
                    "\nVPP F, VPP R: {0:0.2f}  {1:0.2f}".format(float(perfData[0,5]),float(perfData[1,5]))+ \
                    "\nMPP F, MPP R: {0:0.2f}  {1:0.2f}".format(float(perfData[0,6]),float(perfData[1,6]))+ \
                    "\nFF F, FF R: {0:0.2f}  {1:0.2f}".format(float(perfData[0,7]),float(perfData[1,7]))+ \
                    "\nPCE F, PCE R: {0:0.2f}  {1:0.2f}".format(float(perfData[0,8]),float(perfData[1,8]))+ \
                    "\nIllumination: "+perfData[0,9]+ \
                    "\nAcq Soak Voltage: {0:0.2f}".format(float(acqParams.iloc[0]['Acq Soak Voltage']))+ \
                    "\nAcq Soak Time: {0:0.2f}".format(float(acqParams.iloc[0]['Acq Soak Time'])) + \
                    "\nAcq Hold Time: {0:0.2f}".format(float(acqParams.iloc[0]['Acq Hold Time'])) + \
                    "\nAcq Step Voltage: {0:0.2f}".format(float(acqParams.iloc[0]['Acq Step Voltage']))+ \
                    "\nDirection: {0:0.2f}".format(float(acqParams.iloc[0]['Direction']))+ \
                    "\nAcq Rev Voltage: {0:0.2f}".format(float(acqParams.iloc[0]['Acq Rev Voltage']))+ \
                    "\nAcq Forw Voltage: {0:0.2f}".format(float(acqParams.iloc[0]['Acq Forw Voltage']))+ \
                    "\nArchitecture: {0:0.2f}".format(float(acqParams.iloc[0]['Architecture']))+ \
                    "\nDelay Before Meas: {0:0.2f}".format(float(acqParams.iloc[0]['Delay Before Meas']))+ \
                    "\nNum Track Devices: {0:0.2f}".format(float(acqParams.iloc[0]['Num Track Devices']))+ \
                    "\nTrack Time: {0:0.2f}".format(float(acqParams.iloc[0]['Track Time']))+ \
                    "\nHold Track Time: {0:0.2f}".format(float(acqParams.iloc[0]['Hold Track Time']))+ \
                    "\nDevice Area: {0:0.2f}".format(float(acqParams.iloc[0]['Device Area']))+ \
                    "\nComments: "+acqParams.iloc[0]['Comments']+ \
                    "\nOperator: "+acqParams.iloc[0]['Operator']
            
            self.textDatabox.setText(text)
            #except:
            #    print(" Failed to retrieve data from DM.")

    # Get specific device data from DM
    def getDMData(self, row):
        substrate = self.resTableDMWidget.item(row,0).text()
        device = self.resTableDMWidget.item(row,1).text()
        type = self.resTableDMWidget.item(row,2).text()
        
        db, connFlag = self.connectDM()
        if connFlag == False:
            print("Abort")
            return
        if type == "JV" or type == "JV_dark":
            for entry in db.Measurement.find({'substrate':substrate, 'itemId':device}):
                if entry['measType'] == "JV":
                    if entry['name'] == "JV_r":
                        entryR = entry
                    if entry['name'] == "JV_f":
                        entryF = entry
                elif entry['measType'] == "JV_dark":
                    if entry['name'] == "JV_dark_r":
                        entryR = entry
                    if entry['name'] == "JV_dark_f":
                        entryF = entry
        
            perfData = np.array([self.getPerfData(entryR),self.getPerfData(entryF)])

            JV_r = self.getJV(entryR)
            JV_f = self.getJV(entryF)
            JV = np.append(JV_r,JV_f,axis=1)
            acqParams = self.getAcqParams(entryR)

        elif type == "tracking":
            for entry in db.Measurement.find({'substrate':substrate, 'itemId':device, 'measType':'tracking'}):
                perfData = np.array(entry['output'])
                JV = np.array([[0., 0., 0., 0.]])
                acqParams = self.getAcqParams(entry)

        return substrate, device, perfData, JV, acqParams

    # Process entry from DM into perfData
    def getPerfData(self,entry):
        perfData = np.append(entry['Acq Date'],entry['Acq Time'])
        perfData = np.append(perfData,entry['Time step'])
        perfData = np.append(perfData,entry['Voc'])
        perfData = np.append(perfData,entry['Jsc'])
        perfData = np.append(perfData,entry['VPP'])
        perfData = np.append(perfData,entry['MPP'])
        perfData = np.append(perfData,entry['FF'])
        perfData = np.append(perfData,entry['PCE'])
        perfData = np.append(perfData,entry['Light'])
        return perfData
    
    # Process entry from DM into acqParams
    def getAcqParams(self, entry):
        pdframe = pd.DataFrame({'Operator': entry['Operator'],
                'Acq Soak Voltage': entry['Acq Soak Voltage'],
                'Acq Soak Time': entry['Acq Soak Time'],
                'Acq Hold Time': entry['Acq Hold Time'],
                'Acq Step Voltage': entry['Acq Step Voltage'],
                'Direction': entry['Direction'],
                'Acq Rev Voltage': entry['Acq Rev Voltage'],
                'Acq Forw Voltage': entry['Acq Forw Voltage'],
                'Architecture': entry['Architecture'],
                'Delay Before Meas': entry['Delay Before Meas'],
                'Num Track Devices': entry['Num Track Devices'],
                'Track Time': entry['Track Time'],
                'Hold Track Time': entry['Hold Track Time'],
                'Device Area': entry['Device Area'],
                'Comments': entry['Comments']})
        return pdframe[['Acq Soak Voltage','Acq Soak Time','Acq Hold Time',
                'Acq Step Voltage','Acq Rev Voltage','Acq Forw Voltage','Architecture',
                'Direction','Num Track Devices','Delay Before Meas','Track Time',
                'Hold Track Time', 'Device Area', 'Operator','Comments']]
    
    # Enable right click on substrates for saving locally and delete
    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        rPos = self.resTableDMWidget.mapFromGlobal(QCursor.pos())
        if rPos.x()>0 and rPos.x()<self.resTableDMW and \
                rPos.y()>0 and rPos.y()<self.resTableDMH and \
                self.resTableDMWidget.rowCount() > 0 :
        
            selectCellSaveAction = QAction('Save selected data as csv files...', self)
            selectCellSaveAction.setShortcut("Ctrl+s")
            selectCellSaveAllAction = QAction('Save all data as csv files...', self)
            selectCellSaveAllAction.setShortcut("Ctrl+Shift+s")
            viewDMEntryAction = QAction("&View Entry in Database", self)
            viewDMEntryAction.setShortcut("Ctrl+v")
            selectCellRemoveAction = QAction('Remove Selected...', self)
            selectCellRemoveAction.setShortcut("Del")
            selectRemoveAllAction = QAction('Remove All...', self)
            selectRemoveAllAction.setShortcut("Shift+Del")
            self.menu.addAction(selectCellRemoveAction)
            self.menu.addAction(selectRemoveAllAction)
            self.menu.addSeparator()
            self.menu.addAction(selectCellSaveAction)
            self.menu.addAction(selectCellSaveAllAction)
            self.menu.addSeparator()
            self.menu.addAction(viewDMEntryAction)
            self.menu.popup(QCursor.pos())
            QApplication.processEvents()
            
            selectedRows = list(set([ i.row() for i in self.resTableDMWidget.selectedItems()]))
            selectCellSaveAction.triggered.connect(lambda: self.saveLocallyDM(selectedRows))
            selectCellSaveAllAction.triggered.connect(lambda: self.saveLocallyDM(list(range(self.resTableDMWidget.rowCount()))))
            selectCellRemoveAction.triggered.connect(lambda: self.removeDMRows(selectedRows))
            selectRemoveAllAction.triggered.connect(lambda: self.resTableDMWidget.setRowCount(0))
            #viewDMEntryAction.triggered.connect(lambda: self.parent().parent().samplewind.viewOnDM(self.resTableDMWidget.selectedItems()[0].text()))
            viewDMEntryAction.triggered.connect(lambda: self.viewOnDM(selectedRows))

    # Logic to save locally devices selected from DM table
    def saveLocallyDM(self, selectedRows):
        try:
            for row in selectedRows:
                substrate, device, perfData, JV, acqParams = self.getDMData(row)
                self.parent().save_csv(substrate+device, acqParams, perfData, JV)
        except:
            print("Error: cannot be saved")

    # Logic to remove selected from DM table
    def removeDMRows(self, selectedRows):
        for row in selectedRows:
            self.resTableDMWidget.removeRow(row)

    def viewOnDM(self, selectedRows):
        for row in selectedRows:
            self.parent().parent().samplewind.viewOnDM(self.resTableDMWidget.item(row,0).text())
            
    # Format JV data from DM
    def getJV(self,entry):
        JV = np.array(entry['output'])
        return JV

    # Connect to DM
    def connectDM(self):
        self.dbConnectInfo = self.parent().parent().dbconnectionwind.getDbConnectionInfo()
        try:
            conn = DataManagement(self.dbConnectInfo)
            client, _ = conn.connectDB()
            db = client[self.dbConnectInfo[2]]
            #print(" Connected to DM")
            return db, True
        except:
            print(" Connection to DM failed")
            return None, False
