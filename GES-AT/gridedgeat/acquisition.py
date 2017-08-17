'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import numpy as np
import time
from .acquisitionWindow import *
from .resultsWindow import *


class Acquisition():
    def __init__(self):
        #self.acquisitionwind = AcquisitionWindow()
        self.resultswind = ResultsWindow()

    def start(self):
        self.time = 0
        print("Start Aquisition")
        
        self.resultswind.clearPlots()
        
        for i in range(5):
            print("JV #",i+1)
            self.resultswind.processData(self.time, self.generateRandomJV())
            self.resultswind.show()
            self.time = self.time + 1
        print("Acquisition Done")
        
    
    def stop(self):
        print("Not yet implemented")

    ################################################################
    def generateRandomJV(self):
        VStart = 0
        VEnd = 1
        VStep = 0.02
        I0 = 1e-10
        Il = 0.5
        n = 1+ random.randrange(0,20,1)/10
        T = 300
        kB = 1.38064852e-23  # Boltzman constant m^2 kg s^-2 K^-1
        q = 1.60217662E-19  # Electron charge
        
        JV = np.zeros((0,2))
        for i in np.arange(VStart,VEnd,VStep):
            temp = Il - I0*math.exp(q*i/(n*kB*T))
            JV = np.vstack([JV,[i,temp]])
        JV[:,1] = JV[:,1]-np.amin(JV[:,1])
        return JV

    ### This will only be used for testing, to sumulate an actual experiment
    def temporaryAcquisition(self):
        self.time = self.time + 1
        self.processData(self.generateRandomJV())
