"""
Load power spectra for various LIGO noise estimates and measurements.
"""
__author__ = "Leo Singer <leo.singer@ligo.org>"
__all__ = ('psds',)

from numpy import sqrt, loadtxt
import os.path

asd_paths = (
	('LHO (best S5)', 'data/max_H1-TMPLTBANK-871198828-2048.strainspec_asd_v4.txt'),
	('LHO (best S6)', 'data/H1-TMPLTBANK-962268343-2048.strainspec.txt'),
	('high freq', 'data/T0900288/High_Freq.txt'),
	('no SRM', 'data/T0900288/NO_SRM.txt'),
	('BHBH 20deg', 'data/T0900288/BHBH_20deg.txt'),
	('NSNS optimized', 'data/T0900288/NSNS_Opt.txt'),
	('zero det., low power', 'data/T0900288/ZERO_DET_low_P.txt'),
	('zero det., high power', 'data/T0900288/ZERO_DET_high_P.txt'),
)

plotkwargs = {
	'LHO (best S5)': {'color': '0.5', 'linestyle': '-', 'linewidth': 0.5},
	'LHO (best S6)': {'color': 'k', 'linestyle': '-', 'linewidth': 0.5},
	'high freq': {'color': 'k', 'linestyle': ':'},
	'no SRM': {'color': 'k', 'linestyle': '-.'},
	'NSNS optimized': {'color': 'k', 'linestyle': '--'},
	'BHBH 20deg': {'color': '0.5', 'linestyle': '--'},
	'zero det., low power': {'color': '0.5', 'linestyle': '-'},
	'zero det., high power': {'color': 'k', 'linestyle': '-'}
}

asds = tuple( (key, loadtxt(os.path.join(os.path.dirname(__file__), value))) for key, value in asd_paths )

# "LHO (best S6)" actually stores PSD, not ASD.
for name, data in asds:
	if name == 'LHO (best S6)':
		data[:, 1] = sqrt(data[:, 1])