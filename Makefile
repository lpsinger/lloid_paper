TEX = env TEXINPUTS=:$(CURDIR)/packages/iopart:$(CURDIR)/packages/signalflowlibrary:$(CURDIR)/packages: pdflatex -file-line-error -halt-on-error -shell-escape

PREREQS = \
	figures/snr_in_time.pdf figures/bw.pdf figures/bw_resample.pdf figures/lloid-diagram.pdf figures/upsample-symbol.pdf figures/downsample-symbol.pdf figures/adder-symbol.pdf figures/fir-symbol.pdf flop_budget.tex flop_budget_example.tex inspiral_svd.tex introduction.tex implementation.tex conclusions.tex appendix.tex packages.tex macros.tex method.tex results.tex time_slices.pdf mock_psd.pdf time_slices.tex time_slice_latency.tex references.bib

inspiral_svd.pdf: $(PREREQS)
	$(TEX) -draftmode inspiral_svd
	bibtex inspiral_svd
	$(TEX) -draftmode inspiral_svd
	$(TEX) inspiral_svd

figures/snr_in_time.pdf: snr_in_time.py
	python $^ $@

flop_budget.tex: gstlal_flop_budget.py 0.xml
	python $^ > $@

time_slices.tex: time_slices.py matplotlibrc
	python $< --mass1 1.4 --mass2 1.4 --flow 10 > $@

time_slices.pdf time_slice_latency.tex: time_slices.tex
	true # noop, built along with time_slices.tex

mock_psd.pdf: mock_psd.py
	python $<

clean:
	rm -f inspiral_svd.{aux,log,bbl,blg,pdf} time_slices.{tex,pdf} figures/snr_in_time.pdf time_slice_latency.tex mock_psd.pdf flop_budget.tex
