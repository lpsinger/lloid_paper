TEX = env TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj:$(CURDIR)/packages/signalflowlibrary: pdflatex -file-line-error -halt-on-error -shell-escape
BIBTEX = env BSTINPUTS=:$(CURDIR)/packages/astronat/apj: TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj: bibtex

PREREQS = \
	figures/snr_in_time.pdf figures/loc_in_time.pdf figures/tmpltbank.pdf figures/bw.pdf figures/bw_resample.pdf figures/lloid-diagram.pdf figures/upsample-symbol.pdf figures/downsample-symbol.pdf figures/adder-symbol.pdf figures/fir-symbol.pdf inspiral_svd.tex introduction.tex implementation.tex conclusions.tex appendix.tex packages.tex macros.tex method.tex results.tex references.bib

inspiral_svd.pdf: $(PREREQS)
	$(TEX) -draftmode inspiral_svd
	$(BIBTEX) inspiral_svd
	$(TEX) -draftmode inspiral_svd
	$(TEX) inspiral_svd

figures/snr_in_time.pdf: snr_in_time.py
	python $^ $@

figures/loc_in_time.pdf: localization_uncertainty.py
	python $^ $@

clean:
	rm -f inspiral_svd.{aux,out,log,bbl,blg,pdf} time_slices.{tex,pdf} figures/snr_in_time.pdf time_slice_latency.tex mock_psd.pdf
