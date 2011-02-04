#!/usr/bin/env python

# Imports

from optparse import OptionParser, Option
from gstlal.templates import time_slices
import numpy as np

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

# Generate output table

print r"\begin{tabular}{rr@{, }ll}"
print r"\hline\hline"
print r"$f_s$ (Hz) & [$t_\mathrm{end}$ & $t_\mathrm{start}$) & Samples \\"
print r"\hline"
old_rate = None
for slice in slices:
	begin = slice['begin']
	if begin != 0.: # arrgh! floats have both negative and positive 0!
		begin = -begin
	if slice['rate'] == old_rate:
		print r"\dots & [%(end)g&%(begin)g) & %(samples)d \\" % {'begin': begin, 'end': -slice['end'], 'samples': int(round((slice['end'] - slice['begin']) * slice['rate']))}
	else:
		print r"%(rate)d & [%(end)g&%(begin)g) & %(samples)d \\" % {'begin': begin, 'end': -slice['end'], 'rate': slice['rate'], 'samples': int(round((slice['end'] - slice['begin']) * slice['rate']))}
		old_rate = slice['rate']
print r"\hline"
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
