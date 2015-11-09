#
# Written by Joris van Zwieten, zwieten@astron.nl, November 2008
# Version 1.0
#

import numpy

def fetch(db, stations, phasors=False, parm="Gain:11", direction=None,
    asPolar=True):

    suffix = ""
    if direction:
        suffix = ":%s" % direction

    infix = ("Real", "Imag")
    if phasors:
        infix = ("Ampl", "Phase")

    el0 = []
    el1 = []
    for station in stations:
        fqname = "%s:%s:%s%s" % (parm, infix[0], station, suffix)
        el0.append(_fetch_value(db, fqname))

        fqname = "%s:%s:%s%s" % (parm, infix[1], station, suffix)
        el1.append(_fetch_value(db, fqname))

    el0 = numpy.array(el0)
    el1 = numpy.array(el1)

    if phasors and not asPolar:
        re = numpy.zeros(el0.shape)
        im = numpy.zeros(el1.shape)

        for i in range(0, len(stations)):
            re[i] = el0[i] * numpy.cos(el1[i])
            im[i] = el0[i] * numpy.sin(el1[i])

        return (re, im)

    if not phasors and asPolar:
        ampl = numpy.zeros(el0.shape)
        phase = numpy.zeros(el1.shape)

        for i in range(0, len(stations)):
            ampl[i] = numpy.sqrt(numpy.power(el0[i], 2) + numpy.power(el1[i], 2))
            phase[i] = numpy.arctan2(el1[i], el0[i])

        return (ampl, phase)

    return (el0, el1)

def _fetch_value(db, parm):
    tmp = db.getValuesGrid(parm)[parm]
    if type(tmp) is dict:
        return numpy.squeeze(tmp["values"])
    
    # Old parmdb interface.
    return numpy.squeeze(tmp)
