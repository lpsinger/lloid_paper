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

def horizon(Mc, rho2):
	LAL_C = 299792458.
	LAL_PI = 3.1415926535897932384626433832795029
	LAL_MTSUN_SI = 4.9254909500000001e-06
	LAL_PC_SI = 3.0856775807e16
	Mc = Mc * LAL_MTSUN_SI	
	D = 2. * LAL_C * (5./96.)**.5 * Mc**(5./6.) * LAL_PI**(-2./3.) * rho2**.5 / 8.
	return D / 1e6 / LAL_PC_SI

# Horizon
H_ligo = horizon(mchirp, rho2_ligo[-1])
H_virgo = horizon(mchirp, rho2_virgo[-1])

# Scale everything for an SNR of 10 in LIGO detectors
#factor = 1 / rho_ligo[-1]
invS_ligo *= 1 / rho2_ligo[-1]
invS_virgo *= 1 / rho2_virgo[-1]
rho2_ligo *= 1 / rho2_ligo[-1]
rho2_virgo *= 1 / rho2_virgo[-1]

# Effective bandwidth.
# Note an omission in Fairhurst (2009): the frequency moments have to be
# defined with a normalization of 1 / \int |h(f)|^2 / S(f) df, or 1 / SNR.
sigmaf_ligo = numpy.sqrt(numpy.cumsum(f2_weights * invS_ligo) / rho2_ligo - (numpy.cumsum(f1_weights * invS_ligo) / rho2_ligo)**2)
sigmaf_virgo = numpy.sqrt(numpy.cumsum(f2_weights * invS_virgo) / rho2_virgo - (numpy.cumsum(f1_weights * invS_virgo) / rho2_virgo)**2)

# Timing uncertainty
sigmat_ligo = 1. / (2 * pi * rho_threshold * sigmaf_ligo)
sigmat_virgo = 1. / (2 * pi * rho_threshold * sigmaf_virgo)

# Uncertainty in direction cosines in plane of detector
sigmax = sigmat_ligo / 7e-3
sigmay = numpy.sqrt((2 * sigmat_virgo ** 2 + sigmat_ligo ** 2) / 3.) / 22e-3

# Minimum area of 90% confidence region
a90best = 2 * pi * numpy.log(10) * sigmax * sigmay

# time
t = freq_to_time(mchirp, f)

print r"\begin{tabular}{rrrrrr}"
print r"\tableline\tableline"
print r"& horiz. & rate & final & \multicolumn{2}{c}{$A$(90\%) (deg$^2$)} \\"
print r"\cline{5-6}"
print r"$t$ (s) & (Mpc) & (yr$^{-1}$) & \SNR\ & early & final \\"
print r"\tableline"
for t_before_merger in [25., 10, 5., 1., 0.1, 0]:
	rho_final_ligo = rho_threshold / numpy.sqrt(rho2_ligo[t >= t_before_merger][-1])
	rho_final_virgo = rho_threshold / numpy.sqrt(rho2_virgo[t >= t_before_merger][-1])

	sigmat_final_ligo = 1. / (2 * pi * rho_final_ligo * sigmaf_ligo[-1])
	sigmat_final_virgo = 1. / (2 * pi * rho_final_virgo * sigmaf_virgo[-1])

	sigmax_final = sigmat_final_ligo / 7e-3
	sigmay_final = numpy.sqrt((2 * sigmat_final_virgo ** 2 + sigmat_final_ligo ** 2) / 3.) / 22e-3
	a_final = 2 * pi * numpy.log(10) * sigmax_final * sigmay_final * (180 / pi) ** 2

	a = a90best[t >= t_before_merger][-1] * (180 / pi) ** 2

	horizon = H_ligo * (8. / rho_final_ligo)
	rate = 40. * (horizon / H_ligo) ** 3
	print r"%.1f & %.0f & %d & %.1f & %.1f & %.1f \\" % (t_before_merger, horizon, round(rate), rho_final_ligo, a, a_final)
print r"\tableline"
print r"\end{tabular}"


# exceptional event is 1 per year
horizon = H_ligo / 40. ** (1./3.)
rho_threshold = H_ligo * (8. / horizon)

# SNR
rho_ligo = rho2_ligo ** .5
rho_virgo = rho2_virgo ** .5

# Timing uncertainty
sigmat_ligo = 1. / (2 * pi * rho_threshold * rho_ligo * sigmaf_ligo)
sigmat_virgo = 1. / (2 * pi * rho_threshold * rho_virgo * sigmaf_virgo)

# Uncertainty in direction cosines in plane of detector
sigmax = sigmat_ligo / 7e-3
sigmay = numpy.sqrt((2 * sigmat_virgo ** 2 + sigmat_ligo ** 2) / 3.) / 22e-3

# Minimum area of 90% confidence region
a90best = 2 * pi * numpy.log(10) * sigmax * sigmay * (180 / pi) ** 2

fig = pylab.figure(figsize=(3,2))
ax = fig.add_subplot(1,1,1, adjustable='box')
ax.loglog(t[rho_ligo >= 8. / rho_threshold], a90best[rho_ligo >= 8. / rho_threshold], 'k')
for rho in [8., 12., 16., 20.]:
	ax.loglog(t[rho_ligo >= rho / rho_threshold][0], a90best[rho_ligo >= rho / rho_threshold][0], 'k+')
ax.set_xlim(1e-1, 1e2)
ax.axhline(a90best[-1], color='k', linestyle='--')
ax.invert_xaxis()
pylab.ylabel(r'$A$(90%) (deg$^2$)')
pylab.xlabel(r'time before coalescence, $t$ (s)')
pylab.subplots_adjust(bottom=0.2,top=0.95,left=0.2,right=0.95)
pylab.savefig(sys.argv[1])

