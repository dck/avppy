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


for i in xrange(9):
    t = (i + 1) * total / 10
    os.system("ffmpeg -i %s -ss %0.3fs frame%i.png" % (sys.argv[1], t, i))

full = None
for y in xrange(3):
    for x in xrange(3):
        img = Image.open("frame%i.png" % (y*3+x))
        w, h = img.size
        if full is None:
            full = Image.new("RGB", (w*3, h*3))
        full.paste(img, (x*w, y*h))

full.save("thumbs.png")