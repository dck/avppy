#!/usr/bin/env python
# -*- coding= utf-8 -*-

import config as c

import cv

import numpy as np

filename = "./tests/1.mp4"

IMAGE_DEVIATION_TRESHOLD = 2.0

def get_frame_set(file_name, dt, max_frame_count = 10):
    i = 0
    frames = []

    source = cv.CreateFileCapture(file_name)
    frame = cv.QueryFrame(source)

    while(True):
        if len(frames) >= max_frame_count:
            break
        frame = cv.QueryFrame(source)
        if (frame == None):
            break
        if i % dt == 0:
            if get_picture_std(frame) > IMAGE_DEVIATION_TRESHOLD:
                frames.append(cv.CloneImage(frame))
        i+=1
    return frames

def get_picture_std(img):
    return np.array(img).std(axis=1).std()

if __name__ == '__main__':
    frames = get_frame_set(filename, 40, 10)

    cv.NamedWindow("frame", cv.CV_WINDOW_AUTOSIZE)
    loop = True
    while(loop):
        for frame in frames:
            cv.ShowImage("frame", frame)
            char = cv.WaitKey(33)
            if (char != -1):
                if (ord(char) == 27):
                    loop = False  
    cv.DestroyAllWindows()

