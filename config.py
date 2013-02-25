#!/usr/bin/env python
# -*- coding: utf-8 -*-


# video options
convertOptions = {
    "width": 600,
    "height": 450,
    "bitrate": 1800,
    "startoffset": 10, #in seconds
    "pathtofont": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "logotext": "http://asd.com",
    "fontcolor": "white",
    "fontsize": 20,
    "offsetx": -10, # '-' means from left 
    "offsety": -10 # '-' means from low
}
convertCommand = "avconv -i {inputfile} -ss {startoffset} -strict experimental -vf \"drawtext=fontfile={pathtofont}: text='{logotext}':fontcolor={fontcolor}@1.0:fontsize={fontsize}:x={offsetx}:y={offsety}, delogo=x={x}:y={y}:w={w}:h={h}:band=10:show=0\" {outfile}"


# thumbnail options
delay = 2*60 # in seconds


# custom options
folders_thumbnail = "thumbnails"
folders_old       = "old"
folders_result    = "converted"
folders_videos    = "videos"

log_file = "avp.log"
