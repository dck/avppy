#!/usr/bin/env python
# -*- coding= utf-8 -*-

import cv2
import numpy as np
 
c = cap = cv2.VideoCapture("../tests/4.mp4")

_,f = c.read()
f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

avg = np.float32(f)

cv2.namedWindow("img")
cv2.namedWindow("grey")
cv2.namedWindow("avg")

while(1):
    _,f = c.read()

    f = np.float32(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
    cv2.imshow('img',f)

    cv2.accumulateWeighted(f,avg,0.005)
    
    res = cv2.convertScaleAbs(avg)
    
    cv2.imshow('grey',res)

    thresh, res = cv2.threshold(res, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(30,30))
    mat = cv2.dilate(res,kernel)

    contours, hierarchy = cv2.findContours(mat,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    res = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(res, contours,-1,(0,255,0),3)

    cv2.imshow('avg',res)
    k = cv2.waitKey(20)
    if k == 27:
        break
 
cv2.destroyAllWindows()
c.release()
