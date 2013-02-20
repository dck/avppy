#!/usr/bin/env python
# -*- coding= utf-8 -*-

import config as c
import cv
import numpy as np
import PIL
import matplotlib.pyplot as plt

filename = "./tests/test1.mp4"

IMAGE_DEVIATION_TRESHOLD = 10.0

def get_frame_set(file_name, dt, max_frame_count = 10, skip_frames = 20):
    i = 0
    frames = []

    source = cv.CreateFileCapture(file_name)
    frame = cv.QueryFrame(source)

    while(True):
        if i > skip_frames:
            break
        cv.QueryFrame(source)
        i+=1

    while(True):
        if len(frames) >= max_frame_count:
            break
        frame = cv.QueryFrame(source)
        if (frame == None):
            break
        if i % dt == 0:
            treshold = get_picture_std(frame)
            if treshold > IMAGE_DEVIATION_TRESHOLD:
                print treshold
                frames.append(cv.CloneImage(frame))
        i+=1
    return frames

def get_picture_std(img):
    return np.asarray(img[:,:]).std(axis=1).std()

def process(frame_set):
    images = [np.asarray(frame[:,:]) for frame in frame_set]
    sample_images = np.concatenate([image.reshape(1,image.shape[0], image.shape[1],image.shape[2]) 
                                for image in images], axis=0)

    # plt.figure(1)
    # for i in range(sample_images.shape[0]):
    #     plt.subplot(2,2,i+1)
    #     plt.imshow(sample_images[i,...])
    #     plt.axis("off")
    # plt.subplots_adjust(0,0,1,1,0,0)

    # # determine per-pixel variablility, std() over all images
    variability = sample_images.std(axis=0).sum(axis=2)

    # show image of these variabilities
    plt.figure(2)
    plt.imshow(variability, cmap=plt.cm.gray, interpolation="nearest", origin="lower")


    # determine bounding box
    thresholds = [5,10,12]
    colors = ["r", "g", "b"]
    for threshold, color in zip(thresholds, colors): #variability.mean()
        non_empty_columns = np.where(variability.min(axis=0)<threshold)[0]
        non_empty_rows = np.where(variability.min(axis=1)<threshold)[0]
        boundingBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

        # plot and print boundingBox
        bb = boundingBox
        plt.plot([bb[2], bb[3], bb[3], bb[2], bb[2]],
                 [bb[0], bb[0],bb[1], bb[1], bb[0]])
        print boundingBox

    plt.xlim(0,variability.shape[1])
    plt.ylim(variability.shape[0],0)
    plt.legend()

    plt.show()

if __name__ == '__main__':
    frames = get_frame_set(filename, 3, 6, 5)

    cv.NamedWindow("frame", cv.CV_WINDOW_AUTOSIZE)
    loop = True
    while(loop):
        for frame in frames:
            cv.ShowImage("frame", frame)
            char = cv.WaitKey(33)
            if (char == 27):
                loop = False
    cv.DestroyAllWindows()

    process(frames)