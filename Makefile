TEX = env TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj:$(CURDIR)/packages/signalflowlibrary: pdflatex -file-line-error -halt-on-error -shell-escape
BIBTEX = env BSTINPUTS=:$(CURDIR)/packages/astronat/apj: TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj: bibtex

PREREQS = \
	figures/envelope.eps figures/snr_in_time.eps figures/loc_in_time.eps figures/tmpltbank.pdf figures/bw.pdf figures/bw_resample.pdf figures/lloid-diagram.eps figures/upsample-symbol.eps figures/downsample-symbol.eps figures/adder-symbol.eps figures/fir-symbol.eps inspiral_svd.tex introduction.tex prospects.tex method.tex implementation.tex results.tex conclusions.tex appendix.tex packages.tex macros.tex references.bib

inspiral_svd.pdf: $(PREREQS)
	$(TEX) -draftmode inspiral_svd
	$(BIBTEX) inspiral_svd
	$(TEX) -draftmode inspiral_svd
	$(TEX) inspiral_svd

figures/envelope.eps: envelope.py
	python $^ $@

figures/snr_in_time.eps: snr_in_time.py
	python $^ $@

figures/loc_in_time.eps: localization_uncertainty.py
	python $^ $@

clean:
	rm -f inspiral_svd.{aux,out,log,bbl,blg,pdf} time_slices.{tex,pdf} figures/envelope.eps figures/loc_in_time.eps figures/snr_in_time.eps
