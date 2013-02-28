#!/usr/bin/env python
# -*- coding= utf-8 -*-

import cv2
import numpy as np

tracked_contours = {}

count = 0

class Contour():
    def __init__(self, contour):
        self.data = get_contour_data(contour)
        self.data_errors = [4, 4, 4, 4, 10]

    def __hash__(self):
        return hash((self.data[0], self.data[1], self.data[2], self.data[3]))

    def __eq__(self, other):
        for i in range(len(self.data)-1):
            #print "diff: ", abs(self.data[i]-other.data[i])
            if abs(self.data[i]-other.data[i]) > self.data_errors[i]:
                return False
        return True

def get_contour_data(contour):
    xx = np.array([ a[0][0] for a in contour ])
    yy = np.array([ a[0][1] for a in contour ])
    return [xx.min(), yy.min(), xx.max(), yy.max(), cv2.contourArea(contour)]

def check_contours(contours, count):
    to_del = []

    for t in tracked_contours:
        if count % 3 == 0:
            tracked_contours[t] -= 1

        if tracked_contours[t] < 0:
            to_del.append(t)
        
    for d in to_del:
        del tracked_contours[d]
    
    for contour in contours:
        c = Contour(contour)
        if c in tracked_contours:
            tracked_contours[c] += 1
            print tracked_contours[c], c.data[4]
            if tracked_contours[c] > 30:
                return True, c
        else: tracked_contours[c] = 1
    return False, None

def drawContours(contours, img):
    for contour in contours:
        data = get_contour_data(contour)
        cv2.rectangle(img, (data[0], data[1]), (data[2], data[3]), (255,0,0))

def detect(file_name):
    c = cv2.VideoCapture(file_name)

    _,f = c.read()
    f = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)

    avg = np.float32(f)

    cv2.namedWindow("img")
    cv2.namedWindow("grey")
    cv2.namedWindow("avg")

    t = 0
    count = 0

    while(1):
        if t % 5 != 0:
            _,f = c.read()
            if f == None:
                exit(1)
            t+=1
            continue
        count += 1
        t += 1

        _,f = c.read()

        if f == None:
            exit(1)

        cv2.imshow('img',f)

        f = np.float32(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY))
        
        cv2.accumulateWeighted(f, avg, 0.005)
        
        res = cv2.convertScaleAbs(avg)
        
        cv2.imshow('grey',res)

        thresh, res = cv2.threshold(res, 200, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(40,40))
        mat = cv2.dilate(res,kernel)

        contours, hierarchy = cv2.findContours(mat,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
        res = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
        a,b = check_contours(contours, count)
        
        if a == True:
            cv2.rectangle(res, (b.data[0], b.data[1]), (b.data[2], b.data[3]), (0,255,0), 5)
            cv2.imshow('avg',res)
            k = cv2.waitKey(5000)
            break

        drawContours(contours, res)

        cv2.imshow('avg',res)
        k = cv2.waitKey(20)
        if k == 27:
            break
     
    cv2.destroyAllWindows()
    c.release()

if __name__ == "__main__":
    detect("../tests/4.mp4")