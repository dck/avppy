#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from PIL import Image

chout, chin, cherr = os.popen3("ffmpeg -i %s" % sys.argv[1])
out = cherr.read()
dp = out.index("Duration: ")
duration = out[dp+10:dp+out[dp:].index(",")]
hh, mm, ss = map(float, duration.split(":"))
total = (hh*60 + mm)*60 + ss

width = 3
height = 3


# for i in xrange(9):
#     t = (i + 1) * total / 10
os.system("ffmpeg -i {filename} -f image2 -r 1/{dur} frame%d.png".format(filename=sys.argv[1], dur=total/(width*height)))

full = None
for y in xrange(width):
    for x in xrange(height):
        img = Image.open("frame%i.png" % (y*height+x+2))
        w, h = img.size
        if full is None:
            full = Image.new("RGB", (w*width, h*height))
        full.paste(img, (x*w, y*h))

full.save("thumbs.png")