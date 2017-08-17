import numpy as np

def check_alignment(img_data, threshold):
        count = 0
        iMax = np.amax(img_data)
        threshold = threshold*iMax
        for i in np.nditer(img_data):
            if i > threshold:
                count = count + 1
        contrast = 100*count/img_data.size
        print(" Check alignment [%]: {0:0.3f}".format(contrast))
        return "{0:0.3f}".format(contrast), iMax
