#!/usr/bin/env python
# -*- coding= utf-8 -*-

import cv2
import numpy as np
 
c = cap = cv2.VideoCapture("../tests/4.mp4")

_,f = c.read()
res = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

cv2.namedWindow("img")
cv2.namedWindow("res")
cv2.namedWindow("background")

mog = cv2.BackgroundSubtractorMOG(24*60, 1, 0.9, 0.01)

background = np.copy(res)

while(1):
    _,f = c.read()
    f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

    background = mog.apply(f)
    #mog.getBackgroundImage(background)

    cv2.imshow('img',f)
    cv2.imshow('res',res)
    cv2.imshow('background',background)
    k = cv2.waitKey(20)
    if k == 27:
        break
 
cv2.destroyAllWindows()
c.release()