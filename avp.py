#!/usr/bin/env python
# -*- coding= utf-8 -*-

import config as c

import opencv.cv as cv
import opencv.highgui as highgui

import numpy as np

filename = "./tests/1.mp4"

def get_frame_set(file_name, dt, max_frame_count = 10):
    source = highgui.cvCreateFileCapture(file_name)
    frame = highgui.cvQueryFrame(source)
    
    i = 0
    
    frames = []

    while(True):
        if len(frames) >= max_frame_count:
            break

        frame = highgui.cvQueryFrame(source)
        
        if (frame == None):
            break

        if i % dt == 0:
            frames.append(cv.cvCloneImage(frame))
            
        i+=1

    return frames

def get_picture_std(img):
    return np.array(img).std(axis=1).std()

if __name__ == '__main__':
    highgui.cvNamedWindow("frame", highgui.CV_WINDOW_AUTOSIZE)

    loop = True

    frames = get_frame_set(filename, 5, 10)
    for i in range(len(frames)):
        print "frame:", i, "std:", get_picture_std(frames[i])

    while(loop):
        for frame in frames:
            
            highgui.cvShowImage("frame", frame)
            char = highgui.cvWaitKey(33)
            if (char != -1):
                if (ord(char) == 27):
                    loop = False
        
    highgui.cvDestroyAllWindows()
