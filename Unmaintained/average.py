import sys
import pyrap.images

# Name of the output image
outimg = "averaged"

# List of images to average.
list = ["image.i.SB23_BW_G_sub_Dirty.fits","image.i.SB24_BW_G_sub_Dirty.fits","image.i.SB25_BW_G_sub_Dirty.fits","image.i.SB26_BW_G_sub_Dirty.fits","image.i.SB27_BW_G_sub_Dirty.fits"]

# Read pixel data of first image.
img = pyrap.images.image(list[0])
pixels = img.getdata()

print "Creating average image .",
sys.stdout.flush()

# Add pixel data of other images one by one.
for name in list[1:]:
    tmp = pyrap.images.image(name)
    pixels += tmp.getdata()
    del tmp
    print ".",
    sys.stdout.flush()

# Write averaged pixel data
img.saveas(outimg + ".img")
img = pyrap.images.image(outimg + ".img")
img.putdata(pixels / float(len(list)))
img.tofits(outimg + ".fits")
del img

print "done."
sys.stdout.flush()
