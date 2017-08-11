#import cv2
import time, sys
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from datetime import datetime
#from .qt.QtGui import (QImage,QImageReader)

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
        self.image_path = self.image_folder + self.color_image

    def get_image(self):
        return 0

    def save_image(self):
        return 0
        
    def open_image(self):
        #self.imgg = QImage(QImageReader(self.image_path).read())
        self.img_raw = Image.open(self.image_path).convert('L')
        self.imgg = ImageQt(self.img_raw)
        self.img_data = np.asarray(self.img_raw.convert('L'))
        print(self.img_data.shape)
        return self.imgg
    
    def contrast_alignment(self, threshold):
        count = 0
        threshold = threshold*np.amax(self.img_data)
        for i in np.nditer(self.img_data):
            if i > threshold:
                count = count + 1
        contrast = 100*count/self.img_data.size
        return contrast

    def check_alignment(self):
        sumint=np.sum(self.imgg)
        if sumint>10000000:
            print ('Attention: devices and mask might be misaligned')
        else :
            print ('Devices and mask are properly aligned')

    def color_image_name(self):
        return self.image_path


