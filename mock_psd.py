import sys
sys.path.append('../lloid_aligo')

import noisemodels
from scipy import signal
from numpy import cos, pi, sqrt, random
import pylab


# Filter coefficients

b1 = [4e-28]
a1 = [1., -2 * .99995 * cos(2*pi * 9.103 / 16384), .99995**2]

b2 = [1.1e-23, -1.1e-23]
a2 = [1.]

b3 = [1e-27]
a3 = [1., -2 * .999, .999**2]

b4 = [4e-26]
a4 = [1., -2 * .87 * cos(2*pi * 50 / 16384), .87**2]

b5 = [6.5e-24]
a5 = [1, 2*.45, .45**2]

b = [b1, b2, b3, b4, b5]
a = [a1, a2, a3, a4, a5]


# Calculate total filter bank response

h = 0.
for bb, aa in zip(b, a):
	w, hi = signal.freqz(bb, aa, 16384)
	h += abs(hi)**2
h = sqrt(h) * sqrt(16384) * 3. / 4
w *= 16384/(2*pi)


# Generate some colored Gaussian noise

x = random.randn(len(b), 16384*101)
y = sum(signal.lfilter(bb, aa, xx) for bb, aa, xx in zip(b, a, x))
Pxx, freqs = pylab.psd(y[16384:] * sqrt(16384) * 3. / 4, NFFT=16384, Fs=16384, noverlap=4096)

# Read GWINC model

gwinc_f, gwinc_h = dict(noisemodels.asds)['zero det., high power'].T


# Plot

pylab.clf()
pylab.loglog(gwinc_f, gwinc_h, color='0.75', linewidth=10, label='aLIGO noise model')
pylab.loglog(freqs, sqrt(Pxx), '-r', label='filter bank output')
pylab.loglog(w, h / sqrt(16384) * sqrt(2), '-k', label='filter transfer func.')
pylab.xlim(1, 8192)
pylab.ylim(1e-24, 3e-21)
pylab.grid(which='minor')
pylab.grid(which='major')
pylab.legend()
pylab.xlabel('frequency (Hz)')
pylab.ylabel(r'strain amplitude spectral density, $|h(f)|$ $\left(1/\sqrt{\mathrm{Hz}}\right)$')
pylab.title(r'Comparison of noise model and filter bank output')
pylab.savefig('mock_psd.pdf')
