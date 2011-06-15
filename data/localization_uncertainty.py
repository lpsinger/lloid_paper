#!/usr/bin/env python

import numpy
from numpy import pi

f_ligo, a_ligo = numpy.loadtxt('ZERO_DET_high_P.txt').T
f_virgo, a_virgo = numpy.loadtxt('AdV_baseline_sensitivity_12May09.txt').T

# Component masses (in M_sun)
m1 = 1.4
m2 = 1.4

# Total mass
M = m1 + m2

# Chirp mass
mchirp = (m1 * m2)**.6 / (m1+m2)**.2

# Low frequency cutoff
fLOW = 10

# ISCO frequency (equation 3.6, FINDCHIRP paper)
fISCO = 4400 / M

def freq_to_time(Mc,f):
	LAL_MTSUN_SI = 4.9254909500000001e-06
	Mc = Mc * LAL_MTSUN_SI
	return 5. * Mc / 256. * (pi * Mc * f) ** (-8./3.)

# Frequency step in Hz
df = 0.1

# Frequency grid
f = numpy.arange(fLOW, fISCO + df, df)
f0_weights = 4 * df * f ** (-7./3)
f1_weights = 4 * df * f ** (-4./3)
f2_weights = 4 * df * f ** (-1./3)

# Inverse power spectrum
invS_ligo = numpy.interp(f, f_ligo, a_ligo) ** -2
invS_virgo = numpy.interp(f, f_virgo, a_virgo) ** -2

# SNR
rho_ligo = numpy.cumsum(f0_weights * invS_ligo)
rho_virgo = numpy.cumsum(f0_weights * invS_virgo)

# Scale everything for an SNR of 10 in LIGO detectors
factor = 10 / rho_ligo[-1]
rho_ligo *= factor
rho_virgo *= factor
f2_weights *= factor
f1_weights *= factor

# Effective bandwidth.
# Note an omission in Fairhurst (2009): the frequency moments have to be
# defined with a normalization of 1 / \int |h(f)|^2 / S(f) df, or 1 / SNR.
sigmaf_ligo = numpy.sqrt(numpy.cumsum(f2_weights * invS_ligo) / rho_ligo - (numpy.cumsum(f1_weights * invS_ligo) / rho_ligo)**2)
sigmaf_virgo = numpy.sqrt(numpy.cumsum(f2_weights * invS_virgo) / rho_virgo - (numpy.cumsum(f1_weights * invS_virgo) / rho_virgo)**2)

# Timing uncertainty
sigmat_ligo = 1. / (2 * pi * rho_ligo * sigmaf_ligo)
sigmat_virgo = 1. / (2 * pi * rho_virgo * sigmaf_virgo)

# Uncertainty in direction cosines in plane of detector
sigmax = sigmat_ligo / 7e-3
sigmay = numpy.sqrt((2 * sigmat_virgo ** 2 + sigmat_ligo ** 2) / 3.) / 22e-3

# Minimum area of 90% confidence region
a90best = 2 * pi * numpy.log(10) * sigmax * sigmay

# time
t = freq_to_time(mchirp, f)

print '  t   deg^2   %'
print '-----------------'
for t_before_merger in [10, 1, 0.1]:
	a = a90best[t <= t_before_merger][0]
	print '%4.1f %6.1f %5.2f' % (t_before_merger, a * (180 / pi) ** 2, a / (4*pi) * 100)
