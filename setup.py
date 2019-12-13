#!/usr/bin/python
#python setup.py -p /media/DATA/slide-button-not-working.mp4 -f 11999 -t 50 -s /media/DATA/testpics/

import sys
import numpy as np
import cv2
import argparse
from PIL import Image
import os
from os import listdir
from os.path import isfile, join, abspath
import imghdr
import uuid
import shutil
import functools

class FileItem:
    def __init__(self):
        self.h = ""
    def __init__(self, hash1):
        self.h = hash1
    def __repr__(self):
        return " \n\n======== FileItem with hash:%d" % (self.h)

def bitLeftShift(x, e):
    y, z = e
    return x | (y << z)

def avhash(im):
    if not isinstance(im, Image.Image):
        im = Image.open(im)
    im = im.resize((8, 8), Image.ANTIALIAS).convert('L')
    avg = functools.reduce(lambda x,y : x + y, im.getdata()) / 64.
    return functools.reduce(bitLeftShift, enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())), 0)

def hamming(h1, h2):
    h, d = 0, h1 ^ h2
    while d:
        h += 1
        d &= d - 1
    return h
def calculatorHammingBetweenTwoFrame(item1, item2):
    dist = hamming(item1.h, item2.h)
    return dist
def calculatorPercentTheSameTwoFrame(item1, item2):
    dist = calculatorHammingBetweenTwoFrame(item1, item2)
    percent = (64 - dist) * 100 / 64
    return percent
def getItemHasMinimumSize(item1, item2):
    if item1.width < item2.width:
        return item1
    else:
        return item2

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True, help="path to input video path")
    ap.add_argument("-s", "--savepath", required=True, help="path of folder will save images")
    ap.add_argument("-f", "--frame", type=float, default=0, help="frame to start taken")
    ap.add_argument("-e", "--extract", type=bool, default=False, help="Enable extract to image")
    ap.add_argument("-d", "--debug", type=bool, default=False, help="enable show image")
    ap.add_argument("-t", "--threshold", type=float, default=60.0, help="focus measures that fall below this value will be considered 'blurry'")
    ap.add_argument("-rd", "--removeduplicate", type=bool, default=False, help="Enable remove duplicate")
    ap.add_argument("-max", "--percentsame", required = False, default=95, help = "Max percent same value default 95%")
    args = vars(ap.parse_args())
    
    videoPath = args['path']
    cap = cv2.VideoCapture(videoPath)
    
    if not cap.isOpened():
        print ("could not open")
        sys.exit()
    #set video to end, read time length
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, totalFrames - 1)
    timeLength = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 100)
    fps    = cap.get(cv2.CAP_PROP_FPS)
    
    #width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print ("totalFrames= ",totalFrames)
    print ("timeLength= ",timeLength, "s")
    print ("fps= ",fps, "/s")
    print ("======================================")
    enableWrite = bool(args['extract'])
    frameSequence = int(args['frame'])
    savePath = args['savepath']
    debugImg = bool(args['debug'])
    enableRemoveDuplicate = bool(args['removeduplicate'])
    thresholdValue = float(args["threshold"])
    percentSame = int(float(args['percentsame']))
    firstObj = True
    
    
    print ("path:", videoPath)
    print ("Save to:", savePath)
    print ("Frame started:", frameSequence)
    print ("Enable extract:", enableWrite)
    print ("Enable debug:", debugImg)
    print ("Threshold:", thresholdValue)
    print ("Percent the same:", percentSame, "%")
    print ("Remove duplicate:", enableRemoveDuplicate)
    print ("======================================\n\n")
    
    indx = frameSequence
    
    if frameSequence >= totalFrames:
        print ("The frame input out of total frame of video", totalFrames)
        sys.exit()
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameSequence)
    skipByBlur = 0
    
    while(indx < totalFrames):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Display the resulting frame
        indx = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fm = np.max(cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F)))

        if fm < thresholdValue:
            skipByBlur = skipByBlur + 1
            continue

        if enableRemoveDuplicate:
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_im = Image.fromarray(cv2_im)
            hash1 = avhash(pil_im)
            obj = FileItem(hash1)
            if not firstObj:
                percent = calculatorPercentTheSameTwoFrame(obj, lastedObj)
                if percent < percentSame:
                    lastedObj = obj
                if percent >= percentSame:
                    continue
            if firstObj:
                lastedObj = obj
                firstObj = False

        if indx % 100 == 0:
            print ("=> ", ((indx*1.0)/totalFrames)*100, "%")
        
        if enableWrite:
            fileName = str(indx).zfill(5)
            #cv2.imwrite(savePath + fileName + '.png', frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
            cv2.imwrite(savePath + fileName + '.png', frame)

        if debugImg:
            text = "quality"
            cv2.putText(frame, "{}: {:.2f}".format(text, fm), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
            cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print ("end frame ", indx)
    print ("Skip", skipByBlur, " frames by blur")
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
