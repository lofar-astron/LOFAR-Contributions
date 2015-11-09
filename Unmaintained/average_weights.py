# Quick & dirty inverse-variance weighted image averaging.
# John Swinbank, 2010-07-10
import sys
from numpy import average
from pyrap.images import image

image_data = [
    image(file).getdata() for file in sys.argv[2:]
]
result = average(
    image_data, axis=0,
    weights=[1/data.var() for data in image_data]
)
output = image(
    sys.argv[1] + ".img", values=result,
    coordsys=image(sys.argv[2]).coordinates()
)
output.tofits(sys.argv[1] + ".fits")
