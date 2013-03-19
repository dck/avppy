#!/usr/bin/env python
# -*- coding= utf-8 -*-

import sys
import logging
import subprocess
import os
import sys

import config as c

FORMAT = "[%(asctime)19s] %(video)20s | %(message)s"

logging.basicConfig(format=FORMAT, filename=c.log_file, level=logging.INFO, datefmt='%d.%m.%Y %H:%M:%S')

def usage():
    s = """
    Usage: {scriptname} <filename>

    This script removes logo on video, changes resolution,
    converts and watermarks it

        filename - name of video file
    """ .format(scriptname = sys.argv[0])
    print s


def find_logo(video_file):
    logging.info("Finding logo", extra={"video": video_file})      
    return 10, 10, 100, 100

def process_video(**kwargs):
    opts = c.convertOptions
    opts.update(kwargs)
    opts["outfile"] = "{0}/{1}".format(c.folders_result, os.path.basename(opts["inputfile"]))
    opts["startoffset"] = "{:02d}:{:02d}:{:02d}".format(opts["startoffset"] / 3600, opts["startoffset"] / 60, opts["startoffset"])
    if opts["offsetx"] < 0:
        opts["offsetx"] = opts["width"] - (-opts["offsetx"] % opts["width"])
    if opts["offsety"] < 0:
        opts["offsety"] = opts["height"] - (-opts["offsety"] % opts["height"])

    logging.info("Processing video", extra={"video": opts["inputfile"]})
    command = c.convertCommand.format(**opts)
    logging.info("Produced command: {}".format(command), extra={"video": opts["inputfile"]})

    sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdout, stderr) = sub.communicate()
    logging.info(stdout, extra={"video": opts["inputfile"]})

    if  sub.returncode !=0:
        sys.stderr.write("Error occured, see in {}\n".format(c.log_file))
        return False

    return True

def make_thumbnails(video_file):
    logging.info("Making thumbnails", extra={"video": video_file})

if __name__ == '__main__':
    if "--help" in sys.argv or len(sys.argv) < 2:
        usage()
        exit(1)

    video_file = sys.argv[1]
    logging.info("Processing started", extra={"video": video_file})

    x, y, width, height = find_logo(video_file)
    isSuccess = process_video(inputfile = video_file, x = x, y = y, w = width, h = height)
    if isSuccess:
        make_thumbnails(video_file)

    logging.info("Processing finished", extra={"video": video_file})







# import cv
# import numpy as np
# import PIL
# import matplotlib.pyplot as plt

# filename = "./tests/1.mp4"

# IMAGE_DEVIATION_TRESHOLD = 10.0

# def get_frame_set(file_name, dt, max_frame_count = 10, skip_frames = 20):
#     i = 0
#     frames = []

#     source = cv.CreateFileCapture(file_name)
#     frame = cv.QueryFrame(source)

#     while(True):
#         if i > skip_frames:
#             break
#         cv.QueryFrame(source)
#         i+=1

#     while(True):
#         if len(frames) >= max_frame_count:
#             break
#         frame = cv.QueryFrame(source)
#         if (frame == None):
#             break
#         if i % dt == 0:
#             treshold = get_picture_std(frame)
#             if treshold > IMAGE_DEVIATION_TRESHOLD:
#                 print treshold
#                 frames.append(cv.CloneImage(frame))
#         i+=1
#     return frames

# def get_picture_std(img):
#     return np.asarray(img[:,:]).std(axis=1).std()

# def process(frame_set):
#     images = []
#     for frame in frame_set:
#         asd = PIL.Image.fromstring('RGB',cv.GetSize(frame),frame.tostring(),'raw','BGR',frame.width*3,0)
#         images.append(np.asarray(asd))

#     sample_images = np.concatenate([image.reshape(1,image.shape[0], image.shape[1],image.shape[2]) 
#                                 for image in images], axis=0)

#     # plt.figure(1)
#     # for i in range(sample_images.shape[0]):
#     #     plt.subplot(2,2,i+1)
#     #     plt.imshow(sample_images[i,...])
#     #     plt.axis("off")
#     # plt.subplots_adjust(0,0,1,1,0,0)

#     # # determine per-pixel variablility, std() over all images
#     variability = sample_images.std(axis=0).sum(axis=2)

#     # show image of these variabilities
#     plt.figure(2)
#     plt.imshow(variability, cmap=plt.cm.gray, interpolation="nearest", origin="lower")



#     # for i in xrange(len(variability)):
#     #     for j in xrange(len(variability[i])):
#     #         if variability[i][j] > 30:
#     #             variability[i][j] = 255
#     #         else:
#     #             variability[i][j] = 0


#     # determine bounding box
#     thresholds = [5,10,12,16,18,22,25]
#     colors = ["r", "g", "b"] * 3
#     for threshold, color in zip(thresholds, colors): #variability.mean()
#         non_empty_columns = np.where(variability.min(axis=0)<threshold)[0]
#         non_empty_rows = np.where(variability.min(axis=1)<threshold)[0]
#         try:
#             boundingBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
#         except ValueError:
#             print "{} is too small".format(threshold)
#             continue
#         # plot and print boundingBox
#         bb = boundingBox
#         plt.plot([bb[2], bb[3], bb[3], bb[2], bb[2]],
#                  [bb[0], bb[0],bb[1], bb[1], bb[0]])
#         print boundingBox

#     plt.xlim(0,variability.shape[1])
#     plt.ylim(variability.shape[0],0)
#     plt.legend()

#     plt.show()

# if __name__ == '__main__':
#     frames = get_frame_set(filename, 50, 7, 5)

#     # cv.NamedWindow("frame", cv.CV_WINDOW_AUTOSIZE)
#     # loop = True
#     # while(loop):
#     #     for frame in frames:
#     #         cv.ShowImage("frame", frame)
#     #         char = cv.WaitKey(33)
#     #         if (char == 27):
#     #             loop = False
#     # cv.DestroyAllWindows()

#     process(frames)