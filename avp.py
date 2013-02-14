#!/usr/bin/env python
# -*- coding= utf-8 -*-

import config as c

import opencv.cv as cv
import opencv.highgui as highgui
import sys

filename = "./tests/test1.mp4"
#filename = "./tests/test.avi"

if __name__ == '__main__':
	highgui.cvNamedWindow("Example2", highgui.CV_WINDOW_AUTOSIZE)
	capture = highgui.cvCreateFileCapture(filename)
	frame = highgui.cvQueryFrame(capture)

	loop = True
	while(loop):
		frame = highgui.cvQueryFrame(capture)
		if (frame == None):
			break;
		highgui.cvShowImage("Example2", frame)
		char = highgui.cvWaitKey(33)
		if (char != -1):
			if (ord(char) == 27):
				loop = False
	 
	highgui.cvDestroyWindow("Example2")
