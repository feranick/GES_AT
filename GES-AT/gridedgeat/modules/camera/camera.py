'''
cameraFeed.py
-------------
Class for providing a hardware support for 
for the cameraFeed

Copyright (C) 2017 Michel Nasilowski <micheln@mit.edu>
Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

Copyright (C) 2017 Auto-testing team - MIT GridEdge Solar

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import cv2
import time, sys
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from datetime import datetime

class CameraFeed():
    def __init__(self):
        self.camera_port = 0
        self.ramp_frames = 2
        self.image_folder = "images/"
        self.filename = "imagecolor.png"
        self.camera = cv2.VideoCapture(self.camera_port)
        #time.sleep(2)
        self.camera.set(10, -200)
        self.camera.set(15, -8.0)

    def grab_image(self):
        for i in range(self.ramp_frames):
            temp = self.camera.read()
        _, self.img = self.camera.read()
        return self.img

    def get_image(self):
        self.img_raw = Image.fromarray(self.img).convert('L')
        self.imgg = ImageQt(self.img_raw)
        self.img_data = np.asarray(self.img)
        return self.imgg, self.img_data

    def save_image(self, filename):
        cv2.imwrite(self.image_folder + filename,self.img)

    def check_alignment(self, img_data, threshold):
        count = 0
        self.iMax = np.amax(img_data)
        threshold = threshold*self.iMax
        for i in np.nditer(img_data):
            if i > threshold:
                count = count + 1
        contrast = 100*count/img_data.size
        print(" Check alignment [%]: {0:0.3f}".format(contrast))
        return "{0:0.3f}".format(contrast), self.iMax

    def check_alignment_old(self, threshold):
        sumint=np.sum(self.img_data)
        #print(sumint)
        if sumint>10000000:
            print ('Attention: devices and mask might be misaligned')
        else :
            print ('Devices and mask are properly aligned')

    def color_image_name(self):
        return self.image_folder + self.filename

    def close_cam(self):
        del(self.camera)