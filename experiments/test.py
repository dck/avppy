#!/usr/bin/env python
# -*- coding= utf-8 -*-

import cv2
import numpy as np
from time import clock

tracked_contours = []

class Contour():
    def __init__(self, contour):
        self.data = get_contour_data(contour)
        self.pixel_error = 5
        self.score = 0

    def __eq__(self, other):
        for i in range(len(self.data)):
            if abs(self.data[i]-other.data[i]) > self.pixel_error:
                return False
        return True

def get_contour_data(contour):
    xx = np.array([ a[0][0] for a in contour ])
    yy = np.array([ a[0][1] for a in contour ])
    return [xx.min(), yy.min(), xx.max(), yy.max()]

def check_contours(contours, count, img):
    for tracked_contour in tracked_contours:
        if count % 2 == 0:
            tracked_contour.score -= 1

        if tracked_contour.score < 0:
            tracked_contours.remove(tracked_contour)

    for contour in contours:
        c = Contour(contour)
        if c in tracked_contours:
            i = tracked_contours.index(c)
            tracked_contours[i].score += 1
            cv2.rectangle(img, (tracked_contours[i].data[0], \
                tracked_contours[i].data[1]), (tracked_contours[i].data[2], \
                tracked_contours[i].data[3]), (tracked_contours[i].score*10, tracked_contours[i].score*5, tracked_contours[i].score), tracked_contours[i].score)
            if tracked_contours[i].score > 40:
                return True, c
        else: tracked_contours.append(c)

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

        treshold = ((np.max(res)-np.min(res))*0.85)+np.min(res)
        print treshold

        thresh, res = cv2.threshold(res, treshold, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(40,40))
        mat = cv2.dilate(res,kernel)

        contours, hierarchy = cv2.findContours(mat,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
        res = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
        a,b = check_contours(contours, count, res)
        
        if a == True:
            cv2.rectangle(res, (b.data[0], b.data[1]), (b.data[2], b.data[3]), (0,255,0), 5)
            cv2.imshow('avg',res)
            k = cv2.waitKey(5000)
            break

        #drawContours(contours, res)

        cv2.imshow('avg',res)
        k = cv2.waitKey(20)
        if k == 27:
            break
     
    cv2.destroyAllWindows()
    c.release()


class Detector():
    ADD_WEIGHT = 0.005
    MORPH_WEIGHT = (40, 40)
    TRESHOLD = 200
    MAX_SCORE = 40

    def __init__(self, frame):
        self.tick = 0
        self._initAvg(frame)
        self._isDetected = False
        self.trackedContours = []

    def update(self, frame):
        self.tick += 1
        self._updateAvg(frame)
        res = self._getCurrentAvgBinary()
        res = self._applyDilatation(res)
        contours = self._getContours(res)
        self._updateTrackedContours(contours)

    def isDetected(self):
        return self._isDetected

    def getCoords(self):
        max_score = 0
        contour = None
        for trackedContour in self.trackedContours:
            if max_score < trackedContour.score:
                max_score = trackedContour.score
                contour = trackedContour
        if contour != None:
            return [(contour.data[0], contour.data[1]), (contour.data[2], contour.data[3])]
        return None

    def _updateTrackedContours(self, contours):
        for trackedContour in self.trackedContours:
            if self.tick % 2 == 0:
                trackedContour.score -= 1

            if trackedContour.score < 0:
                self.trackedContours.remove(trackedContour)

        for contour in contours:
            c = Contour(contour)
            if c in self.trackedContours:
                i = self.trackedContours.index(c)
                self.trackedContours[i].score += 1
                if self.trackedContours[i].score > Detector.MAX_SCORE:
                    self._isDetected = True
            else: self.trackedContours.append(c)

    def _initAvg(self, frame):
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.avg = np.float32(f)

    def _updateAvg(self, frame):
        frame = np.float32(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        cv2.accumulateWeighted(frame, self.avg, Detector.ADD_WEIGHT)

    def _getCurrentAvgBinary(self):
        res = cv2.convertScaleAbs(self.avg)
        _,res = cv2.threshold(res, Detector.TRESHOLD, 255, cv2.THRESH_BINARY)
        return res            

    def _applyDilatation(self, frame):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, Detector.MORPH_WEIGHT)
        return cv2.dilate(frame, kernel)

    def _getContours(self, frame):
        contours,_ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

def process(fileName):
#    cv2.namedWindow("frame")

    stream = cv2.VideoCapture(fileName)

    _,frame = stream.read()

    detector = Detector(frame)

    t = 0
    while(1):
        if t % 5 != 0:
            _,frame = stream.read()
            if frame == None:
                return detector.getCoords()
            t+=1
            continue
        t += 1

        _,frame = stream.read()

        if frame == None:
            return detector.getCoords()

        detector.update(frame)

        if detector.isDetected():
            return detector.getCoords()
#            returncv2.rectangle(frame, coords[0], coords[1], (0,255,0), 5)
#            cv2.imshow('frame',frame)
#            cv2.waitKey(5000)
            break

#    cv2.destroyAllWindows()
    stream.release()


if __name__ == "__main__":
    fileName = "../tests/3.mp4"
    #detect(fileName)
    print process(fileName)
