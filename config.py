#!/usr/bin/env python
# -*- coding: utf-8 -*-


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