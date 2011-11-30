#!/usr/bin/env python

import sys
from noisemodels import asds, plotkwargs
from pylab import *

fig_width = 3.35
fig_height = 2.75
fig = figure(figsize=(fig_width,fig_height))
for name, data in asds:
	f, asd = data.T
	loglog(f, asd, label=name, **plotkwargs[name])
#legend(loc=(1.05,0.0))
xlabel('frequency ($\mathrm{Hz}$)')
ylabel(r'amplitude spectral density ($1/\sqrt{\mathrm{Hz}}$)')
xlim(9, 3000)
grid(which='minor', color='gray', linewidth=0.1)
grid(linestyle='--', color='k', which='major', linewidth=0.1)
ylim(1e-24, 3e-21)
title('(c) LIGO noise models')
plt.subplots_adjust(bottom=0.45/fig_height,top=1-0.25/fig_height,left=0.75/fig_width,right=(2.4+0.75)/fig_width)
savefig(sys.argv[1], dpi=360)
