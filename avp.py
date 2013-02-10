#!/usr/bin/env python
# -*- coding= utf-8 -*-


actions = {}

actions.convert      = True
actions.cut          = True
actions.delogo       = True
actions.watermarking = True
actions.thumbnails   = True


# video options
width   = 600
height  = 450
bitrate = 1800


# cutting options
startoffset = 10 #in seconds


# watermarking options
logotext = "http://asd.com"
offsetx  = -10 # '-' means from left 
offsety  = -10 # '-' means from low

# thumbnail options
delay = 2*60 # in seconds


# custom options
folders = {}

folders.thumbnail = "thumbnails"
folders.old       = "old"
folders.result    = "converted"



