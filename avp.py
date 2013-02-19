#!/usr/bin/env python
# -*- coding= utf-8 -*-

import config as c

import opencv.cv as cv
import opencv.highgui as highgui

import numpy as np

filename = "./tests/1.mp4"

IMAGE_DEVIATION_TRESHOLD = 2.0

def get_frame_set(file_name, dt, max_frame_count = 10):
    i = 0
    frames = []
    source = highgui.cvCreateFileCapture(file_name)
    while(True):
        if len(frames) >= max_frame_count:
            break
        frame = highgui.cvQueryFrame(source)
        if (frame == None):
            break
        if i % dt == 0:
            if get_picture_std(frame) > IMAGE_DEVIATION_TRESHOLD:
                frames.append(cv.cvCloneImage(frame))
        i+=1
    return frames

def get_picture_std(img):
    return np.array(img).std(axis=1).std()

if __name__ == '__main__':
    frames = get_frame_set(filename, 40, 10)

    highgui.cvNamedWindow("frame", highgui.CV_WINDOW_AUTOSIZE)
    loop = True
    while(loop):
        for frame in frames:
            highgui.cvShowImage("frame", frame)
            char = highgui.cvWaitKey(33)
            if (char != -1):
                if (ord(char) == 27):
                    loop = False    
    highgui.cvDestroyAllWindows()
