#!/usr/bin/env python

from optparse import OptionParser, Option
from pylal import spawaveform
import numpy as np
import matplotlib
from operator import attrgetter
import pylab
from itertools import groupby, izip
import sys

# Command line interface

# Place time slices

# Generate plot
from gstlal.svd_bank import read_bank
bank = read_bank('data/svd_0_9.xml')
pylab.figure(figsize=(2.6,2.5))
ax = pylab.subplot(111)
legend_artists = []
legend_labels = []
num_rates = len(set(x.rate for x in bank.bank_fragments))
tmax = max(x.end for x in bank.bank_fragments)
mc = spawaveform.chirpmass(1.4, 1.4)
for color, (rate, fragments) in izip(pylab.linspace(0.25, 1., num_rates), groupby(bank.bank_fragments, attrgetter('rate'))):
	legend_artists += [pylab.Rectangle((0, 0), 1, 1, facecolor = str(color))]
	legend_labels += ['%d Hz' % rate]
	for fragment in fragments:
		t = pylab.linspace(-fragment.end, -max(fragment.start, 1./4096))
		a = (-0.2 * t / mc) ** (-1./4)
		pylab.fill_between(t, -a, a, facecolor = str(color))
pylab.legend(reversed(legend_artists), reversed(legend_labels), loc='lower left', ncol=2)
pylab.xlim(-tmax, 0.)
pylab.ylim(-.1, .1)
pylab.yticks([], [])
pylab.xticks([-x.end for x in bank.bank_fragments if x.end > 10], [str(x.end) for x in bank.bank_fragments if x.end > 10], rotation=45, size=8.)
pylab.grid()
pylab.xlabel('time relative to coalescence (s)')
pylab.ylabel(r'strain amplitude')
pylab.subplots_adjust(left=0.075, right=0.97, top=0.95, bottom=0.225)
pylab.savefig(sys.argv[1])
