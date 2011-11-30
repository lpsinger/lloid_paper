#!/usr/bin/env python
"""
Plot fractional accumulated SNR versus low frequency cutoff for all noise models.
Also generate tex table and print to stdout.
"""

import sys
from noisemodels import asds, plotkwargs
from pylab import *

# Component mass 1 in M_sun
m1 = 1.4

# Component mass 2 in M_sun
m2 = 1.4

# Total mass in M_sun
M = m1 + m2

# ISCO frequency in Hz
fISCO = 4400 / M

fig_width = 3.35
fig_height = 2.75
fig = figure(figsize=(fig_width,fig_height))

f_lows = range(40, 0, -10)

print r'\begin{tabular}{r' + 'c'*len(f_lows) + '}'
print r'\hline\hline'
print 'Noise model',
for f_low in f_lows:
	print '&', f_low, 'Hz',
print r'\\'
print '\hline'

for i, (name, data) in enumerate(asds):

	# Unpack frequency and amplitue spectral density from array
	f, s = data.T

	# Compute size of frequency bins
	df = diff(f)

	# Mask out values that are less than fISCO or greater than 10 Hz
	mask = (f <= fISCO) & (f >= 10)
	f = f[mask]
	s = s[mask]
	df = df[mask[:-1]]

	# Integrate SNR from f_high down to f_low
	accum_snr = sqrt(cumsum((f**(-7./3) / s**2 * df)[::-1]))[::-1]
	accum_snr /= accum_snr.max()
	accum_snr *= 100

	# Print out row for data table
	print name,
	for f_low in f_lows:
		print '&', '%.1f' % (accum_snr[f.searchsorted(f_low)]),
	print r'\\'

	# Make plot
	plot(f, accum_snr, 'k',
		label=name, **plotkwargs[name])
print '\hline'
print r'\end{tabular}'
	
xlim(80., 0)
ylim(50, 100)
grid(linewidth=0.1)
xlabel('low frequency cutoff $f_\mathrm{low}$ ($\mathrm{Hz}$)')
ylabel('percent accumulated SNR')
title(r'(b) Accumulated SNR vs. $f_\mathrm{low}$')
plt.subplots_adjust(bottom=0.45/fig_height,top=1-0.2/fig_height,left=0.75/fig_width,right=(2.4+0.75)/fig_width)
savefig(sys.argv[1])
