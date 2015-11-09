#
# Run as: casapy --nologger -c casapy2bbs.py <model> [output]
#

import sys

args = sys.argv[4:]
assert(len(args) == 1 or len(args) == 2)

im = ia.newimagefromfile(args[0])

out = sys.stdout
if len(args) == 1:
    out = file("%s.catalog" % args[0], 'w')
elif args[1] != "-":
    out = file(args[1], 'w')

print >>out, "# (Name, Type, Patch, Ra, Dec, I, Q, U, V) = format\n"
print >>out, "# CLEAN component list converted from: %s\n" % args[0]

print >>out, "# Define source patch (patch position is ignored)."
print >>out, ", , CLEAN, 00:00:00, +90.00.00\n"

print >>out, "# Define CLEAN components for the patch."

shape = im.shape()[0:2]
for i in range(0, shape[0]):
    for j in range(0, shape[1]):
        info = im.pixelvalue([i,j])
        flux = info['value']['value']
        if flux == 0.0:
            continue
        ra,dec = im.toworld([i,j], 's')['string'][:2]

        print >>out, "pixel.%d.%d, POINT, CLEAN, %s, %s, %f" % (j, i, ra, dec, flux)

if out != sys.stdout:
    out.close()
