# 20170817 - Joel Jean

from PyAPT import APTMotor
import time
import math

class XYstage():
	def __init__(self):
		'''Initialize X and Y stages'''
		#Initialize stages
		self.SN1 = 45873236
		self.SN2 = 45873513
		self.stage1 = APTMotor(self.SN1, HWTYPE=42, verbose=False) #42 = LTS150/300
		self.stage2 = APTMotor(self.SN2, HWTYPE=42, verbose=False) #42 = LTS150/300
		# Reduce maximum velocity to 15 mm/s
		self.stage1.setVelocityParameters(minVel=0, acc=15, maxVel=15)
		self.stage2.setVelocityParameters(minVel=0, acc=15, maxVel=15)
		# Define distances between adjacent substrates and between adjacent devices, all in mm
		# See interfacedrawings.pdf and Mask Design and Devices page on GridEdge wiki
		self.pitchSub = 25.4 + 4.6 # Substrate width/height + spacing between substrates
		self.pitchDevX = 8 #Distance between center of left and right arms of racetrack
		self.pitchDevY = 4 + 2 #Pad height + spacing between adjacent pads
		# Calculate center positions of all substrates and devices
		self.get_suborigins_4x4()
		self.get_devorigins_3x2()
	

	def get_curr_pos():
	    '''Get current stage position as (x,y) coordinates'''
	    xPos = self.stage1.getPos()
	    yPos = self.stage2.getPos()
	    return [xPos, yPos]

	def move_abs(xPos, yPos):
	    '''Move to the specified position [mm]'''
	    # Include backlash correction
	    self.stage1.mbAbs(xPos)
	    self.stage2.mbAbs(yPos)

	def move_rel(xDelta, yDelta):
	    '''Move relative to current position [mm]'''
	    # Include backlash correction
	    self.stage1.mbRel(xDelta)
	    self.stage2.mbRel(yDelta)

	def move_home():
	    '''Move stages to native (hardware) home positions'''
	    # move_abs(5,5) # Start by moving close to home position to avoid timeout
	    self.stage1.go_home()
	    self.stage2.go_home()

	def set_origin(useCurrPos, newPos):
		'''Set stage origin to current position or specified origin [x,y]'''
		if useCurrPos:
			self.origin = self.get_curr_pos()
		else:
			self.origin = newPos

	def set_ref_cell_origin(useCurrPos, newPos):
		'''Set center position of reference cell to current position or specified position'''
		if useCurrPos:
			self.ref_cell_origin = self.get_curr_pos()
		else:
			self.ref_cell_origin = newPos
			# Example: [self.origin[0] + 5*self.pitchSub, self.origin[1]] = 2 substrate pitches to the right of device 4

	def get_suborigins_4x4():
	    '''Calculate the absolute position of each substrate center'''
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
	    # return subOriginList

	def get_devorigins_3x2():
	    '''Calculate the absolute position of each device center, given list of substrate centers'''
	    # Returns Nsubstrate-long list of 6-long lists of (x,y) positions
	    # |          |
	    # |   ----   |
	    # | 3 |  | 4 |
	    # | 2 |  | 5 |
	    # | 1 |  | 6 |
	    # |   ----   |
	    # |          |
	    self.devOriginList = [[[0,0] for x in range(6)] for y in range(len(subOriginList))]
	    for index,subOrigin in enumerate(self.subOriginList): #Iterate through all substrates (index runs from 0-15)
	        devOrigin1 = [subOrigin[0] - self.pitchDevX/2, subOrigin[1] - self.pitchDevY]
	        devOrigin2 = [subOrigin[0] - self.pitchDevX/2, subOrigin[1]]
	        devOrigin3 = [subOrigin[0] - self.pitchDevX/2, subOrigin[1] + self.pitchDevY]
	        devOrigin4 = [subOrigin[0] + self.pitchDevX/2, subOrigin[1] + self.pitchDevY]
	        devOrigin5 = [subOrigin[0] + self.pitchDevX/2, subOrigin[1]]
	        devOrigin6 = [subOrigin[0] + self.pitchDevX/2, subOrigin[1] - self.pitchDevY]
	        self.devOriginList[index] = [devOrigin1, devOrigin2, devOrigin3, devOrigin4, devOrigin5, devOrigin6]
	    # return devOriginList

	def move_to_substrate_4x4(subIndex):
	    '''Move to the center of the specified substrate (1-16)'''
	    subOrigin = self.subOriginList[subIndex - 1] #Correct for zero-indexing
	    self.move_abs(*subOrigin) #Expand list to individual args (xPos,yPos)
	    return subOrigin

	def move_to_device_3x2(subIndex, devIndex):
	    '''Move to the center of the specified substrate (1-16) and device (1-6)'''
	    devOrigin = self.devOriginList[subIndex - 1][devIndex - 1] #Correct for zero-indexing
	    self.move_abs(*devOrigin) #Expand list to individual args (xPos,yPos)
	    return devOrigin

	def scan_selected_substrates(subsToScanList, waitTime):
	    '''Move to center of each device on specified substrates'''
	    for subIndex in subsToScanList:
	        for devIndex in range(1,7):
	            devOrigin = self.move_to_device_3x2(self.devOriginList, subIndex, devIndex)
	            print('S', subIndex, 'D', devIndex, ': ', devOrigin)
	            time.sleep(waitTime)  # Pause for 1 second at each position

	def end_stage_control():
	    '''Clean up APT objects and free up memory'''
	    self.stage1.cleanUpAPT()
	    self.stage2.cleanUpAPT()
