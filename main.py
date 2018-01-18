#coding:utf-8
import os
import sys
import model
import numpy as np
from PIL import Image
import numpy as np
import time

def main(image_file):
    im = Image.open(image_file)
    img = np.array(im.convert('RGB'))
    t = time.time()
    result,img = model.model(img,model='keras')
    print "It takes time:{}s".format(time.time()-t)
    print "---------------------------------------"
    for key in result:
        print result[key][1]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Please input a parameter'
        exit

    file_name = sys.argv[1]
    if os.path.isfile(file_name):
        main(file_name)
    else:
        print '{} is not a file, please input an image file'.format(file_name)
