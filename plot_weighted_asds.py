#!/usr/bin/env python

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

for name, data in asds:

	# Unpack frequency and amplitue spectral density from array
	f, s = data.T

	# Compute size of frequency bins
	df = diff(f)

	# Mask out values that are less than fISCO or greater than 10 Hz
	mask = (f <= fISCO) & (f >= 10)
	f = f[mask]
	s = s[mask]
	df = df[mask[:-1]]

	weighted_psd = f**(-7./3) / (s * s)
	weighted_psd /= sum(weighted_psd * df)

	# Make plot
	plot(f, weighted_psd, label=name, **plotkwargs[name])

xlim(0, 300)
grid(linewidth=0.1)
xlabel('frequency ($\mathrm{Hz}$)')
ylabel(r'normalized power spectral density')
title('(b) Signal to noise per unit frequency')
plt.subplots_adjust(bottom=0.45/fig_height,top=1-0.2/fig_height,left=0.75/fig_width,right=(2.4+0.75)/fig_width)
savefig(sys.argv[1])
