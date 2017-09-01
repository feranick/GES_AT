'''
XYstage.py
-------------
Class for providing a hardware support for 
for the XYstage

Version: 20170817

Copyright (C) 2017 Joel Jean <jjean@mit.edu>
Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import time, math
try:
    from gridedgeat.modules.xystage.PyAPT import APTMotor
except ImportError:
    pass

class XYstage():
    # Initialize X and Y stages
    def __init__(self):
        #Initialize stages
        self.SN1 = 45873236
        self.SN2 = 45873513
        try:
            self.stage1 = APTMotor(self.SN1, HWTYPE=42, verbose=False) #42 = LTS150/300
            self.stage2 = APTMotor(self.SN2, HWTYPE=42, verbose=False) #42 = LTS150/300
            self.xystageInit = True
        except:
            self.xystageInit = False
            return
            
        # Reduce maximum velocity to 15 mm/s
        self.stage1.setVelocityParameters(minVel=0, acc=15, maxVel=15)
        self.stage2.setVelocityParameters(minVel=0, acc=15, maxVel=15)
        # Define distances between adjacent substrates and between adjacent devices, all in mm
        # See interfacedrawings.pdf and Mask Design and Devices page on GridEdge wiki
        self.pitchSub = 25.4 + 4.6 # Substrate width/height + spacing between substrates
        self.pitchDevX = 8 #Distance between center of left and right arms of racetrack
        self.pitchDevY = 4 + 2 #Pad height + spacing between adjacent pads
        # Calculate center positions of all substrates and devices
        print("Homing stage")
        self.move_home()
        self.move_abs(3,3)
        self.set_origin(True, [0,0])
        self.get_suborigins_4x4()
        self.get_devorigins_3x2()

    # Get current stage position as (x,y) coordinates
    def get_curr_pos(self):
        xPos = self.stage1.getPos()
        yPos = self.stage2.getPos()
        return [xPos, yPos]

    # Move to the specified position [mm]
    def move_abs(self, xPos, yPos):
        # Include backlash correction
        self.stage1.mbAbs(xPos)
        self.stage2.mbAbs(yPos)

    # Move relative to current position [mm]
    def move_rel(self, xDelta, yDelta):
        # Include backlash correction
        self.stage1.mbRel(xDelta)
        self.stage2.mbRel(yDelta)

    # Move stages to native (hardware) home positions
    def move_home(self):
        # move_abs(5,5) # Start by moving close to home position to avoid timeout
        self.stage1.go_home()
        self.stage2.go_home()

    # Set stage origin to current position or specified origin [x,y]
    def set_origin(self, useCurrPos, newPos):
        if useCurrPos:
            self.origin = self.get_curr_pos()
        else:
            self.origin = newPos
            
    # Set center position of reference cell to current position or specified position
    def set_ref_cell_origin(self, useCurrPos, newPos):
        if useCurrPos:
            self.ref_cell_origin = self.get_curr_pos()
        else:
            self.ref_cell_origin = newPos
            # Example: [self.origin[0] + 5*self.pitchSub,
            # self.origin[1]] = 2 substrate pitches to the right of device 4

    # Calculate the absolute position of each substrate center
    def get_suborigins_4x4(self):
        # xIndex:  1 ==> 4   yIndex:
        # 13 | 14 | 15 | 16     4
        # 9  | 10 | 11 | 12     3
        # 5  | 6  | 7  | 8      2
        # 1  | 2  | 3  | 4      1
        self.subOriginList = [[0,0] for x in range(16)] #Create list of (x,y) pairs
        for subIndex in range(1,17):
            xIndex = (subIndex - 1) % 4 + 1
            yIndex = math.ceil(subIndex / 4)
            xPos = self.origin[0] + (xIndex - 1) * self.pitchSub
            yPos = self.origin[1] + (yIndex - 1) * self.pitchSub
            self.subOriginList[subIndex - 1] = [xPos, yPos]
            #return subOriginList

    # Calculate the absolute position of each device center, given list of substrate centers
    def get_devorigins_3x2(self):
        # Returns Nsubstrate-long list of 6-long lists of (x,y) positions
        # |          |
        # |   ----   |
        # | 3 |  | 4 |
        # | 2 |  | 5 |
        # | 1 |  | 6 |
        # |   ----   |
        # |          |
        self.devOriginList = [[[0,0] for x in range(6)] for y in range(len(self.subOriginList))]
        # Iterate through all substrates (index runs from 0-15)
        for index,subOrigin in enumerate(self.subOriginList):
            devOrigin1 = [subOrigin[0] - self.pitchDevX/2, subOrigin[1] - self.pitchDevY]
            devOrigin2 = [subOrigin[0] - self.pitchDevX/2, subOrigin[1]]
            devOrigin3 = [subOrigin[0] - self.pitchDevX/2, subOrigin[1] + self.pitchDevY]
            devOrigin4 = [subOrigin[0] + self.pitchDevX/2, subOrigin[1] + self.pitchDevY]
            devOrigin5 = [subOrigin[0] + self.pitchDevX/2, subOrigin[1]]
            devOrigin6 = [subOrigin[0] + self.pitchDevX/2, subOrigin[1] - self.pitchDevY]
            self.devOriginList[index] = [devOrigin1,
                devOrigin2, devOrigin3, devOrigin4, devOrigin5, devOrigin6]
        #return devOriginList

    # Move to the center of the specified substrate (1-16)
    def move_to_substrate_4x4(self, subIndex):
        # Correct for zero-indexing
        subOrigin = self.subOriginList[subIndex - 1]
        # Expand list to individual args (xPos,yPos)
        self.move_abs(*subOrigin)
        return subOrigin
    
    # Move to the center of the specified substrate (1-16) and device (1-6)
    def move_to_device_3x2(self, subIndex, devIndex):
        # Correct for zero-indexing
        devOrigin = self.devOriginList[subIndex - 1][devIndex - 1]
        # Expand list to individual args (xPos,yPos)
        self.move_abs(*devOrigin)
        return devOrigin

    # Move to center of each device on specified substrates
    def scan_selected_substrates(self, subsToScanList, waitTime):
        for subIndex in subsToScanList:
            for devIndex in range(1,7):
                devOrigin = self.move_to_device_3x2(self.devOriginList, subIndex, devIndex)
                print('S', subIndex, 'D', devIndex, ': ', devOrigin)
                # Pause for 1 second at each position
                time.sleep(waitTime)
    
    # Clean up APT objects and free up memory
    def end_stage_control(self):
        self.stage1.cleanUpAPT()
        self.stage2.cleanUpAPT()
