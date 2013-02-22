#!/usr/bin/env python
# -*- coding: utf-8 -*-


action_convert      = True
action_cut          = True
action_delogo       = True
action_watermarking = True
action_thumbnails   = True


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
folders_thumbnail = "thumbnails"
folders_old       = "old"
folders_result    = "converted"

log_file = "avp.log"
