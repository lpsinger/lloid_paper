#!/usr/bin/env python

# Imports

from optparse import OptionParser, Option
from gstlal.templates import time_slices
from pylal import spawaveform
import numpy as np
import matplotlib
import pylab
from itertools import groupby, izip
matplotlib.rcParams.update({
        "figure.figsize": (3,2.8),
        "subplots.left": 0.1,
        "subplots.right": 0.75,
        "subplots.bottom": 0.25,
        "subplots.top": 0.75,
		"legend.fontsize": 8.0
})

# Command line interface

opts, args = OptionParser(description = __doc__, option_list = [
	Option("--mass1", type="float", metavar="solar masses", help="component mass 1"),
	Option("--mass2", type="float", metavar="solar masses", help="component mass 2"),
	Option("--flow", type="float", metavar="Hz", help="low frequency cutoff"),
]).parse_args()

if len(args) > 0:
	raise ValueError("Too many arguments")

for key in ("mass1", "mass2", "flow"):
	if getattr(opts, key) is None:
		raise ValueError("Required argument --%s is missing" % key)

# Place time slices

fhigh = 4400. / (opts.mass1 + opts.mass2)
mass_pairs = ((opts.mass1, opts.mass2), )
slices = time_slices(mass_pairs, opts.flow, fhigh)
mc = spawaveform.chirpmass(opts.mass1, opts.mass2)

# Generate plot
pylab.figure()
ax = pylab.subplot(111)
tmin = min(slice['begin'] for slice in slices)
tmax = max(slice['end'] for slice in slices)
legend_artists = []
legend_labels = []
rate_key = lambda x: x['rate']
num_rates = len(set([x[0] for x in sorted(slices, key = rate_key)]))
for color, (rate, more_slices) in izip(pylab.linspace(1., 0., num_rates), groupby(sorted(slices, key = rate_key), key = rate_key)):
	legend_artists += [pylab.Rectangle((0, 0), 1, 1, facecolor = str(color))]
	legend_labels += ['%d Hz' % rate]
	for slice in more_slices:
		t = pylab.arange(-slice['end'], -slice['begin'])
		a = (-0.2 * t / mc) ** (-1./4)
		pylab.fill_between(t, -a, a, facecolor = str(color))
		pylab.axvline(-slice['end'], color = 'k', linestyle = ':')
pylab.yticks([], [])
pylab.legend(legend_artists, legend_labels, loc = 'lower left')
pylab.xlim(-tmax, 0.)
pylab.ylim(-.15, .15)
pylab.xlabel('time relative to coalescence (s)')
pylab.ylabel(r'gravitational wave strain amplitude')
matplotlib.pyplot.subplots_adjust(left=0.06, right=0.88, top=0.95, bottom=0.13)

pylab.savefig('time_slices.pdf')


# Generate output table

print r"\begin{tabular}{lrr}"
#FIXME change the symbol for the number of sample points per slice if the macro changes
print r"$f^s$ (Hz) & $\left(t^{s+1}, t^s\right]$ (s) & $\slicessamps$ \\"
print r"\hline"
for slice in slices:
	begin = slice['begin']
	print r"%(rate)d & $(%(end)g, %(begin)g]$ & %(samples)d \\" % {'begin': begin, 'end': slice['end'], 'rate': slice['rate'], 'samples': int(round((slice['end'] - slice['begin']) * slice['rate']))}
print r"\end{tabular}"

# Write latency

print >>open("time_slice_latency.tex", "w"), (r"%g~\mathrm{s}" % max(2 * (slice['end'] - slice['begin']) - slice['begin'] for slice in slices)),

# Write operation count

rank_reduction = 0.1
block_length_factor = 2.
resample_kernel_length = 64
kernel_length = (slices['end'] - slices['begin']) * slices['rate']
raw_kernel_length = (max(slices['end']) - min(slices['begin'])) * max(slices['rate'])
print >>open("time_slice_ops_firslice.tex", "w"), r"%d" % int(2 * len(slices) + round(sum(slices['rate'] / float(max(slices['rate'])) * ((8. * np.log2(block_length_factor * kernel_length) + 2) / (1 - 1. / block_length_factor) + 4 * resample_kernel_length))))
print >>open("time_slice_ops_conv.tex", "w"), r"%d" % int(round( (8 * np.log2(block_length_factor * raw_kernel_length) + 2) / (1 - 1. / block_length_factor)))
print >>open("time_slice_ops_td.tex", "w"), r"%.1f \times 10^6" % (2 * raw_kernel_length * 1e-6)
