#!/usr/bin/env python

import sys
from noisemodels import asds, plotkwargs
from pylab import *

fig_width = 7.
fig_height = 0.75
fig = figure(figsize=(fig_width,fig_height))
for name, data in asds:
	plot([0, 1], [0, 1], label=name.replace('deg', '$^\circ$').replace('det.', 'detuning'), **plotkwargs[name])
legend(loc=(0.,-1.5), ncol=3)
ax = gca()
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.subplots_adjust(bottom=0.4,top=0.6,left=0.75/fig_width,right=(2.5+0.75)/fig_width)
savefig(sys.argv[1])
