from PIL import Image
import numpy as _np if False else None
Image.new("L",(7,5),128).save("/tmp/gray8.png")
Image.new("LA",(7,5),(128,200)).save("/tmp/gray_a.png")
Image.new("P",(7,5),3).save("/tmp/pal.png")
Image.new("RGB",(7,5),(10,20,30)).save("/tmp/rgb.png")
Image.new("1",(7,5),1).save("/tmp/bw.png")
Image.new("I;16",(7,5),1000).save("/tmp/g16.png")
print([ (f, os.path.getsize(f)) for f in ["/tmp/gray8.png","/tmp/gray_a.png","/tmp/pal.png","/tmp/rgb.png","/tmp/bw.png","/tmp/g16.png"]])
