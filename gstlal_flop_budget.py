#!/usr/bin/env python
"""Floating point operation count budgets for LLOID."""
__author__ = "Leo Singer <leo.singer@ligo.org>"
# FIXME: are we counting a multiply-accumulate as one operation or two?


import math
import sys


#
# Miscellaneous utility functions.
#


def lg(x):
	"""Logarithm base 2."""
	return math.log(x) / math.log(2.)


#
# Operation counts for convolution (or cross correlation) filters.
#


def td_conv_ops(kernel_len, count_channels=1):
	"""Calculate the number of floating point operations per sample required to
	apply a convolution filter with a kernel of kernel_len samples and
	count_channels channels, using the FIR (time domain) implementation."""

	# One multiply and one add per sample.
	return 2 * kernel_len * count_channels


def fd_conv_ops(kernel_len, block_len_factor=2, count_channels=1):
	"""Calculate the number of floating point operations per sample required to
	apply a convolution filter with a kernel of kernel_len samples and
	count_channels channels, using the FFT (frequency domain) implementation and
	a block size of (block_len) or (block_len_factor * kernel_len)."""

	# 1 forward FFT and count_channels inverse FFTs
	ops = 4 * lg(kernel_len * block_len_factor) * (count_channels + 1)

	# count_channels dot products
	ops += 2 * count_channels

	# (1/block_len_factor) of the data gets reused from one block to the next
	ops /= (1 - 1. / block_len_factor)

	return ops


#
# Operation counts for miscellaneious signal processing operations.
#


def resample_filter_ops(kernel_len, in_rate, out_rate, count_channels=1):
	"""Calculate the number of floating point operations per sample require to
	apply an FIR resampling filter."""

	# no-op if in_rate == out_rate
	if in_rate == out_rate:
		return 0

	# FIR filter...
	ops = td_conv_ops(kernel_len, count_channels)

	# ... but (min(rates) / max(rates)) of the samples are zero.
	ops *= float(min(in_rate, out_rate)) / max(in_rate, out_rate)

	return ops


#
# Operation counts for LLOID methods.
#


def td_conv_time_slice_ops(kernel_lens, rates, resample_kernel_len=192, count_channels=1):
	"""Calculate the numebr of floating point operations per sample required to
	apply a multirate convolution filter with kernels of length kernel_lens,
	sample rates given by rates, and resampling filters with kernels of length
	resample_kernel_len."""

	max_rate = max(rates)
	ops = 0

	for kernel_len, rate in zip(kernel_lens, rates):
		# downsample
		ops += resample_filter_ops(resample_kernel_len, max_rate, rate, count_channels)
		# convolution
		ops += td_conv_ops(kernel_len, count_channels) * float(rate) / max_rate
		# upsample
		ops += resample_filter_ops(resample_kernel_len, rate, max_rate, count_channels)
		# accumulate filter output
		ops += count_channels

	return ops


def fd_conv_time_slice_ops(kernel_lens, rates, block_len_factor=2, resample_kernel_len=192, count_channels=1):
	"""Calculate the numebr of floating point operations per sample required to
	apply a multirate convolution filter with kernels of length kernel_lens,
	sample rates given by rates, and resampling filters with kernels of length
	resample_kernel_len."""

	max_rate = max(rates)
	ops = 0

	for kernel_len, rate in zip(kernel_lens, rates):
		# downsample
		ops += resample_filter_ops(resample_kernel_len, max_rate, rate, count_channels)
		# convolution
		ops += fd_conv_ops(kernel_len, block_len_factor, count_channels) * float(rate) / max_rate
		# upsample
		ops += resample_filter_ops(resample_kernel_len, rate, max_rate, count_channels)
		# accumulate filter output
		ops += count_channels

	return ops


def fd_lloid_ops(L, M, N, rates, block_len_factor=2, resample_kernel_len=192, reconstruction_duty_cycle=0.05):

	max_rate = max(rates)
	ops = 0

	for count_channels, kernel_len, rate in zip(L, M, rates):
		# downsample
		ops += resample_filter_ops(resample_kernel_len, max_rate, rate)
		# convolution
		ops += fd_conv_ops(kernel_len, block_len_factor, count_channels) * float(rate) / max_rate
		# compute composite detection statistic for this slice (squaring, multiplying by weight)
		ops += 3 * count_channels * float(rate) / max_rate
		# upsample composite detection statistic for this slice
		ops += resample_filter_ops(resample_kernel_len, rate, max_rate)
		# accumulate composite detection statistic
		ops += 1

		# conditional reconstruction: count_channels x N matrix multiply
		conditional_ops = 2 * count_channels * N * float(rate) / max_rate
		# upsample reconstructed SNR from this slice
		conditional_ops += resample_filter_ops(resample_kernel_len, rate, max_rate, N)
		# accumulate reconstructed SNR
		conditional_ops += N

		ops += reconstruction_duty_cycle * conditional_ops

	return ops


def fd_lloid_cascade_ops(L, M, N, rates, block_len_factor=2, resample_kernel_len=64, reconstruction_duty_cycle=0.05):

	max_rate = max(rates)
	old_rate = None
	ops = 0

	for rate, count_channels, kernel_len in sorted(zip(rates, L, M)):
		# downsample
		ops += resample_filter_ops(resample_kernel_len, max_rate, rate)
		# convolution
		ops += fd_conv_ops(kernel_len, block_len_factor, count_channels) * float(rate) / max_rate
		# compute composite detection statistic for this slice (squaring, multiplying by weight)
		ops += 3 * count_channels * float(rate) / max_rate
		# upsample composite detection statistic for this slice
		ops += resample_filter_ops(resample_kernel_len, rate, max_rate)
		# accumulate composite detection statistic
		ops += 1

		# conditional reconstruction: count_channels x N matrix multiply
		conditional_ops = 2 * count_channels * N * float(rate) / max_rate
		# upsample reconstructed SNR from this slice
		if old_rate is not None:
			if old_rate != rate:
				conditional_ops += resample_filter_ops(resample_kernel_len, old_rate, rate, N) * float(rate) / max_rate
			# accumulate reconstructed SNR
			conditional_ops += N * float(rate) / max_rate

		ops += reconstruction_duty_cycle * conditional_ops
		old_rate = rate

	return ops


def fd_lloid_cascade_2_ops(L, M, N, rates, block_len_factor=2, resample_kernel_len=64, reconstruction_duty_cycle=0.05):

	max_rate = max(rates)
	old_rate = None
	ops = 0

	for rate, count_channels, kernel_len in sorted(zip(rates, L, M)):
		# downsample
		ops += resample_filter_ops(resample_kernel_len, max_rate, rate)
		# convolution
		ops += fd_conv_ops(kernel_len, block_len_factor, count_channels / 2) * float(rate) / max_rate
		# compute composite detection statistic for this slice (squaring, multiplying by weight)
		ops += 2.5 * count_channels * float(rate) / max_rate
		# upsample composite detection statistic for this slice
		ops += resample_filter_ops(resample_kernel_len, rate, max_rate)
		# accumulate composite detection statistic
		ops += 1

		# conditional reconstruction: count_channels x N matrix multiply
		conditional_ops = 2 * count_channels * N * float(rate) / max_rate / 2.
		# upsample reconstructed SNR from this slice
		if old_rate is not None:
			if old_rate != rate:
				conditional_ops += resample_filter_ops(resample_kernel_len, old_rate, rate, N) * float(rate) / max_rate
			# accumulate reconstructed SNR
			conditional_ops += N * float(rate) / max_rate

		ops += reconstruction_duty_cycle * conditional_ops
		old_rate = rate

	return ops


def td_lloid_ops(L, M, N, rates, resample_kernel_len=192, reconstruction_duty_cycle=0.05):

	max_rate = max(rates)
	ops = 0

	for count_channels, kernel_len, rate in zip(L, M, rates):
		# downsample
		ops += resample_filter_ops(resample_kernel_len, max_rate, rate)
		# convolution
		ops += td_conv_ops(kernel_len, count_channels) * float(rate) / max_rate
		# compute composite detection statistic for this slice (squaring, multiplying by weight)
		ops += 3 * count_channels * float(rate) / max_rate
		# upsample composite detection statistic for this slice
		ops += resample_filter_ops(resample_kernel_len, rate, max_rate)
		# accumulate composite detection statistic
		ops += 1

		# conditional reconstruction: count_channels x N matrix multiply
		conditional_ops = 2 * count_channels * N * float(rate) / max_rate
		# upsample reconstructed SNR from this slice
		conditional_ops += resample_filter_ops(resample_kernel_len, rate, max_rate, N)
		# accumulate reconstructed SNR
		conditional_ops += N

		ops += reconstruction_duty_cycle * conditional_ops

	return ops




if __name__ == '__main__':
	"""Example that reads in an SVD'd template bank and prints out some operation counts."""

	def prettyprint_int(n, sep=' '):
		# FIXME: only works for positive numbers.
		s = ""
		while n > 0:
			n, r = divmod(n, 1000)
			if n > 0:
				s = "%c%03d%s" % (sep, r, s)
			else:
				s = "%d%s" % (r, s)
		return s

	def prettyprint_sci(f):
		f = r"%.1e"%f
		s = r"$"
		s += f.split('e')[0]
		s += r" \times 10^{"
		s += r"%i"%int(f.split('e')[-1])
		s += r"}$"
		return s

	from optparse import Option, OptionParser
	opts, args = OptionParser(usage = '%prog file').parse_args()

	if len(args) > 1:
		raise ValueError("Expected exactly one argument.")

	from gstlal.svd_bank import read_bank
	frags = read_bank(args[0]).bank_fragments

	L, M, rates = zip(*[(frag.mix_matrix.shape[0], int(frag.rate * (frag.end - frag.start)), frag.rate) for frag in frags])
	N = frags[0].mix_matrix.shape[1]
	raw_kernel_length = (max(frag.end for frag in frags) - min(frag.start for frag in frags)) * max(rates)

	latencies = {}
	latencies['fir'] = 1./max(rates)
	latencies['fft'] = max([frag.end for frag in frags])
	latencies['fft_slice'] = min([frag.end for frag in frags])

	print r"\begin{tabular}{r c l}"
	print r"\hline\hline"
	print r"operations/sample & latency (s.) & method \\"
	print r"\hline"
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(td_conv_ops(raw_kernel_length, count_channels=N)))), prettyprint_sci(latencies['fir']), r"conventional \textsc{fir} method")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_conv_ops(raw_kernel_length, count_channels=N)))), prettyprint_sci(latencies['fft']), r"conventional \textsc{fft} method")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(td_lloid_ops([int(N/3.)], [raw_kernel_length], N, [max(rates)], reconstruction_duty_cycle=1.)))), prettyprint_sci(latencies['fir']), r"\textsc{fir} method with \textsc{svd}")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_lloid_ops([int(N/3.)], [raw_kernel_length], N, [max(rates)], reconstruction_duty_cycle=1.)))), prettyprint_sci(latencies['fft']), r"\textsc{fft} method with \textsc{svd}")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(td_lloid_ops([int(N/3.)], [raw_kernel_length], N, [max(rates)])))), prettyprint_sci(latencies['fir']), r"\textsc{fir} method with \textsc{lloid} and no time slices")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_lloid_ops([int(N/3.)], [raw_kernel_length], N, [max(rates)])))), prettyprint_sci(latencies['fft']), r"\textsc{fft} method with \textsc{lloid} and no time slices")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(td_conv_time_slice_ops(M, rates, count_channels=N)))), prettyprint_sci(latencies['fir']), r"\textsc{fir} method with time slices")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_conv_time_slice_ops(M, rates, count_channels=N)))), prettyprint_sci(latencies['fft_slice']), r"\textsc{fft} method with time slices")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(td_lloid_ops(L, M, N, rates, reconstruction_duty_cycle=1.)))), prettyprint_sci(latencies['fir']), r"\textsc{fir} method with time slices and \textsc{svd}")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_lloid_ops(L, M, N, rates, reconstruction_duty_cycle=1.)))), prettyprint_sci(latencies['fft_slice']), r"\textsc{fft} method with time slices and \textsc{svd}")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(td_lloid_ops(L, M, N, rates)))), prettyprint_sci(latencies['fir']), r"\textsc{fir} method with \textsc{lloid}")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_lloid_ops(L, M, N, rates)))), prettyprint_sci(latencies['fft_slice']), r"\textsc{fft} method with \textsc{lloid}")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_lloid_cascade_ops(L, M, N, rates)))), prettyprint_sci(latencies['fft_slice']), r"same, with cascade topology")
	print r"%16s & %s & %s \\" % (prettyprint_int(int(round(fd_lloid_cascade_2_ops(L, M, N, rates)))), prettyprint_sci(latencies['fft_slice']), r"same, with cascade topology 2")
	print r"\hline"
	print r"\end{tabular}"
