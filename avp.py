#!/usr/bin/env python
# -*- coding= utf-8 -*-

import sys
import logging
import subprocess
import os
import sys
import cv2
import glob

import numpy as np
from PIL import Image

############################################################################
################################ Options ###################################

# video options
convertOptions = {
    "width": 600,
    "height": 450,
    "bitrate": 900*1024, # bits/sec
    "startoffset": 10, # in seconds
    "pathtofont": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "logotext": "asd.com",
    "fontcolor": "white",
    "fontsize": 20,
    "offsetx": -10, # '-' means from left 
    "offsety": -10 # '-' means from low
}
convertCommand = "ffmpeg -i {inputfile} -y -strict experimental -s {width}:{height} -b {bitrate} -ss {startoffset} -vcodec libx264 -acodec copy -vf \"drawtext=fontfile={pathtofont}:text='{logotext}':fontcolor={fontcolor}@1.0:fontsize={fontsize}:x={offsetx}:y={offsety}, delogo=x={x}:y={y}:w={w}:h={h}:band=10:show=0\" {outfile}"


# thumbnail options
thumbnails_width  = 3
thumbnails_height = 3


# custom options
folders_thumbnail = "thumbnails"
folders_old       = "old"
folders_result    = "converted"

log_file = "avp.log"

# logo detection algorithm parameters
FRAME_ADD_WEIGHT = 0.005
MORPH_RADIOUS = 20
TRESHOLD = 0.8 # relative
MAX_CONTOUR_SCORE = 40

FORMAT = "[%(asctime)19s] %(video)20s | %(message)s"
logging.basicConfig(format=FORMAT, filename=log_file, level=logging.INFO, datefmt='%d.%m.%Y %H:%M:%S')
WORKFOLDER = os.path.abspath(os.path.dirname(sys.argv[0]))

############################################################################
############################ Logo finder ###################################

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
    def __init__(self, frame):
        self.tick = 0
        self._initAvg(frame)
        self._isDetected = False
        self.trackedContours = []

    def update(self, frame, max_contour_score, frame_add_weight, morph_radious, treshold):
        self.tick += 1
        self._updateAvg(frame, frame_add_weight)
        res = self._getCurrentAvgBinary(treshold)
        res = self._applyDilatation(res, morph_radious)
        contours = self._getContours(res)
        self._updateTrackedContours(contours, max_contour_score)

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

    def _updateTrackedContours(self, contours, max_contour_score):
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
                if self.trackedContours[i].score > max_contour_score:
                    self._isDetected = True
            else: self.trackedContours.append(c)

    def _initAvg(self, frame):
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.avg = np.float32(f)

    def _updateAvg(self, frame, frame_add_weight):
        frame = np.float32(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        cv2.accumulateWeighted(frame, self.avg, frame_add_weight)

    def _getCurrentAvgBinary(self, treshold):
        res = cv2.convertScaleAbs(self.avg)
        min, max = np.min(self.avg), np.max(self.avg)
        _,res = cv2.threshold(res, ((max-min)*treshold)+min, 255, cv2.THRESH_BINARY)
        return res

    def _applyDilatation(self, frame, morph_radious):
        morph_radious *= 2;
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morph_radious, morph_radious))
        return cv2.dilate(frame, kernel)

    def _getContours(self, frame):
        contours,_ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

def find_logo(fileName, max_contour_score, frame_add_weight, morph_radious, treshold):
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

        detector.update(frame, max_contour_score, frame_add_weight, morph_radious, treshold)

        if detector.isDetected():
            return detector.getCoords()
            break

    stream.release()

############################################################################
############################## Other logics ################################

def usage():
    s = """
    Usage: {scriptname} <filename>

    This script removes logo on video, changes resolution,
    converts and watermarks it

        filename - name of video file
    """ .format(scriptname = sys.argv[0])
    print s

def process_video(**kwargs):
    opts = convertOptions
    opts.update(kwargs)
    conv_f =  os.path.join(WORKFOLDER, folders_result)
    opts["outfile"] = "{0}/{1}".format(conv_f, os.path.basename(opts["inputfile"]))
    opts["startoffset"] = "{:02d}:{:02d}:{:02d}".format(opts["startoffset"] / 3600, opts["startoffset"] / 60, opts["startoffset"])
    if opts["offsetx"] < 0:
        opts["offsetx"] = opts["width"] - (-opts["offsetx"] % opts["width"])
    if opts["offsety"] < 0:
        opts["offsety"] = opts["height"] - (-opts["offsety"] % opts["height"])

    logging.info("Processing video", extra={"video": opts["inputfile"]})
    command = convertCommand.format(**opts)
    logging.info("Produced command: {}".format(command), extra={"video": opts["inputfile"]})

    sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdout, stderr) = sub.communicate()
    logging.info(stdout, extra={"video": opts["inputfile"]})

    if  sub.returncode !=0:
        sys.stderr.write("Error occured, see in {}\n".format(log_file))
        return False

    return True

def make_thumbnails(video_file):
    logging.info("Making thumbnails", extra={"video": video_file})
    chout, chin, cherr = os.popen3("ffmpeg -i %s" % sys.argv[1])
    out = cherr.read()
    dp = out.index("Duration: ")
    duration = out[dp+10:dp+out[dp:].index(",")]
    hh, mm, ss = map(float, duration.split(":"))
    total = (hh*60 + mm)*60 + ss

    width = thumbnails_width
    height = thumbnails_height

    screen_folder = os.path.abspath(os.path.dirname(sys.argv[0]))

    os.system("ffmpeg -i {filename} -f image2 -r 1/{dur} {folder}/{imagename}.%d.png".format(filename=sys.argv[1],
                                                                                   dur=total/(width*height),
                                                                                   folder = screen_folder,
                                                                                   imagename=os.path.basename(video_file)))

    full = None
    for y in xrange(width):
        for x in xrange(height):
            img = Image.open("%s/%s.%i.png" % (screen_folder, os.path.basename(video_file), (y*height+x+2)))
            w, h = img.size
            if full is None:
                full = Image.new("RGB", (w*width, h*height))
            full.paste(img, (x*w, y*h))

    thum_f =  os.path.join(WORKFOLDER, folders_thumbnail)
    full.save(os.path.join(thum_f, os.path.basename(video_file) + ".png"))

    for i in glob.glob("{}/{}*.png".format(screen_folder, os.path.basename(video_file))):
        os.remove(i)

def prepare_folders():
    conv_f =  os.path.join(WORKFOLDER, folders_result)
    thum_f =  os.path.join(WORKFOLDER, folders_thumbnail)
    old_f =  os.path.join(WORKFOLDER, folders_old)

    folder_list = [conv_f, thum_f, old_f]
    for f in folder_list:
        if not os.path.exists(f):
            os.makedirs(f)

if __name__ == '__main__':
    if "--help" in sys.argv or len(sys.argv) < 2:
        usage()
        exit(1)
    prepare_folders()
    video_file = sys.argv[1]
    logging.info("Processing started", extra={"video": video_file})

    x, y, width, height = find_logo(video_file, MAX_CONTOUR_SCORE, FRAME_ADD_WEIGHT, MORPH_RADIOUS, TRESHOLD)
    isSuccess = process_video(inputfile = video_file, x = x, y = y, w = width, h = height)
    if isSuccess:
        make_thumbnails(video_file)

    old_f =  os.path.join(WORKFOLDER, folders_old)
    os.rename(video_file, os.path.join(old_f, os.path.basename(video_file)))

    logging.info("Processing finished", extra={"video": video_file})
