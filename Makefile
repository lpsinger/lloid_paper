TEX = env TEXINPUTS=:packages/iopart:packages/signalflowlibrary:packages: pdflatex -file-line-error -halt-on-error
MAKEFILES = figures

PREREQS = \
	figures/lloid-diagram.pdf figures/upsample-symbol.pdf figures/downsample-symbol.pdf figures/adder-symbol.pdf figures/fir-symbol.pdf flop_budget.tex flop_budget_example.tex inspiral_svd.tex introduction.tex analysis.tex conclusions.tex appendix.tex packages.tex macros.tex method.tex results.tex time_slices.pdf mock_psd.pdf time_slices.tex time_slice_latency.tex references.bib N_before_Tc.pdf

inspiral_svd.pdf: $(PREREQS)
	$(TEX) -draftmode inspiral_svd
	bibtex inspiral_svd
	$(TEX) -draftmode inspiral_svd
	$(TEX) inspiral_svd

figures/lloid-diagram.pdf figures/upsample-symbol.pdf figures/downsample-symbol.pdf figures/adder-symbol.pdf figures/fir-symbol.pdf:
	$(MAKE) -C $(@D) $(@F)

flop_budget.tex: gstlal_flop_budget.py 0.xml
	python $^ > $@

time_slices.tex time_slices.pdf time_slice_latency.tex: time_slices.py
	python $< --mass1 1.4 --mass2 1.4 --flow 10 > $@

mock_psd.pdf: mock_psd.py
	python $<

N_before_Tc.pdf: snr_in_time.py
	python $<

clean:
	rm -f inspiral_svd.{aux,log,bbl,blg,pdf} time_slices.{tex,pdf} time_slice_latency.tex mock_psd.pdf flop_budget.tex
	$(MAKE) -C figures $@
