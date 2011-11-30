#!/usr/bin/env python

import sys
from pylal.xlal import constants
from pylab import *

# Component mass 1 in M_sun
m1 = 1.4

# Component mass 2 in M_sun
m2 = 1.4

# Total mass in M_sun
M = m1 + m2

# Chirp mass
Mchirp = (m1 * m2) ** 0.6 * M ** -0.2

# ISCO frequency in Hz
fISCO = 4400. / M

def freq_for_time(t):
	return (t / (5 * Mchirp * constants.LAL_MTSUN_SI)) ** (-3./8) / (8 * pi * Mchirp * constants.LAL_MTSUN_SI)

def time_for_freq(f):
	return 5 * (8 * pi) ** (-8./3) * (Mchirp * constants.LAL_MTSUN_SI) ** (-5./3) * f ** (-8./3)

fig_width = 3.35
fig_height = 2.75
fig = figure(figsize=(fig_width,fig_height))
f = arange(1., 100., 1.)
loglog(f, time_for_freq(f) - time_for_freq(fISCO), 'k', linewidth=1)
for f_low in arange(10., 50., 10.):
	axvline(f_low, color='k', linewidth=1)
	plot([f_low], time_for_freq(f_low), 'o', markersize=5, markeredgewidth=1, markerfacecolor='none', markeredgecolor='k')
	annotate('%d s' % round(time_for_freq(f_low)), (f_low, time_for_freq(f_low)), xytext=(4, 8), textcoords='offset points', backgroundcolor='white')

xlim(10, 100)
ylim(10, 10000)
grid(which='minor', linewidth=0.1)
grid(which='major', linestyle='--', color='k')
xlabel('low frequency cutoff $f_\mathrm{low}$ ($\mathrm{Hz}$)')
ylabel('signal duration from $f=f_\mathrm{low}$ to $f_\mathrm{ISCO}$')


#twiny()
#xlim(1, 100)
#ylim(10, 10000)
#xscale('log')
#yscale('log')
xticks( (1, 10, 20, 30, 40, 100), ('1 Hz', '10 Hz', '20', '30', '40', '100'))

title(r'(d) Inspiral duration vs. $f_\mathrm{low}$')
plt.subplots_adjust(bottom=0.45/fig_height,top=1-0.25/fig_height,left=0.75/fig_width,right=(2.4+0.75)/fig_width)
savefig(sys.argv[1])
