#!/usr/bin/python
import numpy
import matplotlib
matplotlib.use('Agg')
import pylab
import scipy
from scipy import interpolate
import sys

#
# default plot paramaters
#

matplotlib.rcParams.update({
	"font.size": 9.0,
	"axes.titlesize": 9.0,
	"axes.labelsize": 9.0,
	"xtick.labelsize": 9.0,
	"ytick.labelsize": 9.0,
	"legend.fontsize": 9.0,
	"figure.figsize": (3,3),
	"figure.dpi": 600,
	"subplots.left": 0.05,
	"subplots.right": 0.95,
	"subplots.bottom": 0.05,
	"subplots.top": 0.95,
	"savefig.dpi": 600,
	"text.usetex": True     # render all text with TeX
})

#
# Constants
#

LAL_MTSUN_SI = 4.9254909500000001e-06
PI = 3.14159265

#
# Mchirp
#

def mchirp(m1, m2):
        return (m1 * m2)**.6 / (m1+m2)**.2

#
# cumulative fractional snr computed over f
#

def snr(f, asd):
	df = f[1] - f[0]
	out = numpy.cumsum(df * f**(-7./3) / asd(f)**2)**.5
	return out# / out[-1]

#
# frequency to time relationship assuming 0PN 
#

def freq_to_time(Mc,f):
	Mc = Mc * LAL_MTSUN_SI
	return 5. * Mc / 256. * (PI * Mc * f) ** (-8./3.)

#
# the number of events above fractional snr of SNR assuming number detectable
#

def snr_to_num(fracsnr, number=40):
	return number * (fracsnr)**3

# Start a new figure
fig = pylab.figure(1, figsize=(5.5,2.25))

markers = ['k-', 'k--', 'k-.']

snrd = {}

# loop over the noise curves
# ZERO_DET_high_P.txt must be first since it normalizes the rate
for i, cfile in enumerate(['data/ZERO_DET_high_P.txt', 'data/ZERO_DET_low_P.txt', 'data/BHBH_20deg.txt']):

	# Load the data
	A = numpy.loadtxt(cfile)

	# interpolate the asd
	asd = interpolate.interp1d(A[:,0], A[:,1])

	# set up the frequency boundaries
	fmin = 10.
	fmax = 1570. #FIXME allow different masses?

	# define a frequency array
	f = numpy.linspace(fmin, fmax, 10000)

	# compute the snr on the frequency array
	snrd[cfile] = snr(f, asd)

	# normalize all snrs to 'data/ZERO_DET_high_P.txt'
	snr1 = snrd[cfile] / snrd['data/ZERO_DET_high_P.txt'][-1]

	# get the compliment snr from fmax down to f
	# SNRs add in quadrature
	snrminus = (1-snr1**2)**.5

	# work out the time to coalescence at a given f
	t = freq_to_time(mchirp(1.4,1.4),f) # FIXME dont hardcode masses

	# compute the number of sources detectable 
	num = snr_to_num(snr1, number=40)
	numplus = snr_to_num(snr1, number=400)
	numminus = snr_to_num(snr1, number=.4)

	# generate the figure
	ax1 = fig.add_subplot(1,1,1, adjustable='box', aspect=0.5)
	pylab.loglog(t, num, markers[i], lw=2, label=cfile.replace('.txt','').replace('data/','').replace('_','\\_'))
	#pylab.hold(1)
	pylab.fill_between(t, numminus, numplus, color='k', alpha=0.15)

pylab.grid()
pylab.legend(loc='lower left')
pylab.ylabel('$\\langle N \\rangle$ yr$^{-1}$')
pylab.xlabel('$T_{bc}$')
pylab.subplots_adjust(bottom=0.15,top=0.95,left=0.08,right=0.95)
pylab.xlim([0.01,1000])
pylab.ylim([.1, 1000])
pylab.savefig('N_before_Tc.pdf')
sys.exit()