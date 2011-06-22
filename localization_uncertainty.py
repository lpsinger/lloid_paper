#!/usr/bin/env python

import numpy
from numpy import pi
import pylab
import sys

def float_as_string(num, sigfigs = 2):
	"""Convert a floating point number to a string in scientific notation,
	with sigfigs significant figures, suitable for a LaTeX document."""
	import decimal
	with decimal.localcontext() as ctx:
		ctx.prec = 2
		ctx.rounding = decimal.ROUND_HALF_UP
		sci_str = str(decimal.Decimal(str(num)) + decimal.Decimal('0'))

		sci_str_parts = sci_str.split('E')
		if len(sci_str_parts) == 1:
			return sci_str
		elif len(sci_str_parts) == 2:
			return r"\ensuremath{%s \times 10^{%s}}" % (sci_str_parts[0],
				sci_str_parts[1].lstrip('+'))


f_ligo, a_ligo = numpy.loadtxt('data/ZERO_DET_high_P.txt').T
f_virgo, a_virgo = numpy.loadtxt('data/AdV_baseline_sensitivity_12May09.txt').T
# f_ET, a_ET = numpy.loadtxt('data/ET_D_data.txt', usecols=(0,3)).T # not checked in

# Some constants
LAL_C = 299792458.
LAL_PI = 3.1415926535897932384626433832795029
LAL_MTSUN_SI = 4.9254909500000001e-06
LAL_PC_SI = 3.0856775807e16


# Component masses (in M_sun)
m1 = 1.4
m2 = 1.4

# Total mass
M = m1 + m2

# Chirp mass
mchirp = (m1 * m2)**.6 / (m1+m2)**.2

# Low frequency cutoff
fLOW = 2

# ISCO frequency (equation 3.6, FINDCHIRP paper)
fISCO = 4400 / M

def freq_to_time(Mc,f):
	Mc = Mc * LAL_MTSUN_SI
	return 5. * Mc / 256. * (pi * Mc * f) ** (-8./3.)

# Frequency step in Hz
df = 0.01

# Frequency grid
f = numpy.arange(fLOW, fISCO + df, df)
f0_weights = 4 * df * f ** (-7./3)
f1_weights = 4 * df * f ** (-4./3)
f2_weights = 4 * df * f ** (-1./3)

# Inverse power spectrum
invS_ligo = numpy.interp(f, f_ligo, a_ligo) ** -2
invS_virgo = numpy.interp(f, f_virgo, a_virgo) ** -2

# SNR
rho_threshold = 8
rho2_ligo = numpy.cumsum(f0_weights * invS_ligo)
rho2_virgo = numpy.cumsum(f0_weights * invS_virgo)

def horizon(Mc, hdoth):
	Mc = Mc * LAL_MTSUN_SI	
	D = 2. * LAL_C * (5./96.)**.5 * Mc**(5./6.) * LAL_PI**(-2./3.) * hdoth**.5 / 8
	return D / 1e6 / LAL_PC_SI

# Horizon
H_ligo = horizon(mchirp, rho2_ligo[-1])
# H_virgo = horizon(mchirp, rho2_virgo[-1]) # not used

# Scale everything for an SNR of 1 in each detector (just to prevent floating point overflow)
invS_ligo *= 1 / rho2_ligo[-1]
invS_virgo *= 1 / rho2_virgo[-1]
rho2_ligo *= 1 / rho2_ligo[-1]
rho2_virgo *= 1 / rho2_virgo[-1]

# SNR
rho_ligo = numpy.sqrt(rho2_ligo)
rho_virgo = numpy.sqrt(rho2_virgo)

# Effective bandwidth.
# Note an omission in Fairhurst (2009): the frequency moments have to be
# defined with a normalization of 1 / \int |h(f)|^2 / S(f) df, or 1 / SNR.
sigmaf_ligo = numpy.sqrt(numpy.cumsum(f2_weights * invS_ligo) / rho2_ligo - (numpy.cumsum(f1_weights * invS_ligo) / rho2_ligo)**2)
sigmaf_virgo = numpy.sqrt(numpy.cumsum(f2_weights * invS_virgo) / rho2_virgo - (numpy.cumsum(f1_weights * invS_virgo) / rho2_virgo)**2)

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

def localization_uncertainty_as_str(a90):
	if a90 >= 4 * 180**2 / numpy.pi:
		return "-"
	elif a90 < 10:
		return "%.1f" % a90
	elif a90 < 100:
		return "%d" % round(a90)
	elif a90 < 1000:
		return "%d" % (round(a90/10) * 10)
	else:
		return "%d" % (round(a90/100) * 100)

print r"\begin{tabular}{rrrrrrr}"
print r"\tableline\tableline"
print r"rate & horiz. & final & \multicolumn{4}{c}{$A$(90\%) (deg$^2$)} \\"
print r"\cline{4-7}"
print r"yr$^{-1}$ & (Mpc) & \SNR\ & 25 s & 10 s & 1 s & 0 s \\"
print r"\tableline"
for rate in (40., 10., 1., 0.1):
	final_snr = rho_threshold * (40. / rate) ** (1./3)
	a90 = a90best / final_snr ** 2 * (180. / pi) ** 2
	a90_25 = localization_uncertainty_as_str(a90[t >= 25][-1])
	a90_10 = localization_uncertainty_as_str(a90[t >= 10][-1])
	a90_1 = localization_uncertainty_as_str(a90[t >= 1][-1])
	a90_0 = localization_uncertainty_as_str(a90[t >= 0][-1])
	horizon = H_ligo * (8. / final_snr)
	print r"%g & %d & %.1f & %s & %s & %s & %s \\" % (rate, round(horizon), final_snr, a90_25, a90_10, a90_1, a90_0)
print r"\tableline"
print r"\end{tabular}"


fig = pylab.figure(figsize=(3,2))
ax = fig.add_subplot(1,1,1, adjustable='box')

for rate in (40., 10., 1., 0.1):
	final_snr = rho_threshold * (40. / rate) ** (1./3)
	pred = rho_ligo * final_snr >= rho_threshold
	a90 = a90best / final_snr ** 2 * (180. / pi) ** 2
	pylab.loglog(t[~pred], a90[~pred], ':k')
	pylab.loglog(t[pred][0], a90[pred][0], 'ok', markersize=3)
	pylab.loglog(t[pred], a90[pred], 'k')
	pylab.text(.8*t[-1], a90[-1], r"%g yr$^{-1}$" % rate, {"size": 8.}, horizontalalignment='left', verticalalignment='center')
pylab.xlim(0., 1000.)
pylab.ylim(1e-1, 41253)
ax.invert_xaxis()
pylab.grid()
pylab.ylabel(r'$A$(90%) (deg$^2$)')
pylab.xlabel(r'time before coalescence, $t$ (s)')
pylab.subplots_adjust(bottom=0.2,top=0.95,left=0.2,right=0.85)
pylab.savefig(sys.argv[1])
