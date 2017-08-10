#import cv2
import time, sys
import numpy as np
from PIL import Image
from datetime import datetime

class CameraFeed():
    def __init__(self):
        self.camera_port = 1
        self.ramp_frames = 30
        self.camera = cv2.VideoCapture(self.camera_port)
        time.sleep(2)
        self.camera.set(10, -200)
        self.camera.set(15, -8.0)
        self.image_folder = "images/"
        self.color_image = "imagecolor"

    def get_image(self):
        retval, im = self.camera.read()
        return im

    def save_image(self):
        for i in range(self.ramp_frames):
            temp = self.camera.read()

        camera_capture = self.get_image()
        self.filename = self.color_image+str(datetime.now().strftime('_%Y-%m-%d_%H-%M-%S.png'))
        cv2.imwrite(self.filename,camera_capture)
        del(self.camera)
        
    def open_image(self):
        self.imgc = Image.open(self.image_folder + self.filename)
        self.imgc.show()

        self.imgg = Image.open(self.image_folder + filename).convert('L')
        self.greyfilename = "grey_" + filename
        self.imgg.save(self.image_folder + self.greyfilename)
        self.imgg.show()

    def check_alignment(self):
        sumint=np.sum(self.imgg)
        #print(sumint)
        if sumint>10000000:
            print ('Attention: devices and mask might be misaligned')
        else :
            print ('Devices and mask are properly aligned')

    def color_image_name(self):
        return self.image_folder + filename

    def grey_img_name(self):
        return self.image_folder + self.greyfilename


class CameraFeedTemp():
    def __init__(self):
        self.image_folder = "images/"
        self.color_image = "imagecolor.png"

    def get_image(self):
        return 0

    def save_image(self):
        return 0
        
    def open_image(self):
        self.imgg = Image.open(self.image_folder + self.color_image).convert('L')
        self.imgg.show()

    def check_alignment(self):
        sumint=np.sum(self.imgg)
        if sumint>10000000:
            print ('Attention: devices and mask might be misaligned')
        else :
            print ('Devices and mask are properly aligned')

    def color_image_name(self):
        return self.image_folder + self.color_image

