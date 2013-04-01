#!/usr/bin/env python
# -*- coding= utf-8 -*-

import cv2
import numpy as np
from time import clock

class Contour():
    PIXEL_ERROR_SIZE = 5

    def __init__(self, contour):
        self.data = self.get_contour_data(contour)
        self.score = 0

    def __eq__(self, other):
        for i in range(len(self.data)):
            if abs(self.data[i]-other.data[i]) > Contour.PIXEL_ERROR_SIZE:
                return False
        return True

    def get_contour_data(self, contour):
        xx = np.array([ a[0][0] for a in contour ])
        yy = np.array([ a[0][1] for a in contour ])
        return [xx.min(), yy.min(), xx.max(), yy.max()]


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
            return [contour.data[0], contour.data[1], contour.data[2]-contour.data[0], contour.data[3]-contour.data[1]]
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
            break

    stream.release()


if __name__ == "__main__":
    fileName = "./tests/1.avi"
    print process(fileName)
