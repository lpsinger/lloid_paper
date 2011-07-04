TEX = env TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj:$(CURDIR)/packages/signalflowlibrary: pdflatex -file-line-error -halt-on-error -shell-escape
BIBTEX = env BSTINPUTS=:$(CURDIR)/packages/astronat/apj: TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj: bibtex

FIGURES = f1.eps f2.eps f3.eps f3a.eps f3b.eps f3c.eps f3d.eps f4.eps f5a.eps f5b.eps t3.eps
PREREQS = \
	$(FIGURES) inspiral_svd.tex introduction.tex prospects.tex method.tex implementation.tex results.tex conclusions.tex appendix.tex packages.tex macros.tex references.bib

inspiral_svd.pdf: $(PREREQS)
	$(TEX) -draftmode inspiral_svd
	$(BIBTEX) inspiral_svd
	$(TEX) -draftmode inspiral_svd
	$(TEX) inspiral_svd

f1.eps: snr_in_time.py
	python $^ $@

f2.eps: localization_uncertainty.py
	python $^ $@

f3.eps: figures/lloid-diagram.eps
	ln -s $^ $@

f3a.eps: figures/upsample-symbol.eps
	ln -s $^ $@

f3b.eps: figures/downsample-symbol.eps
	ln -s $^ $@

f3c.eps: figures/adder-symbol.eps
	ln -s $^ $@

f3d.eps: figures/fir-symbol.eps
	ln -s $^ $@

f4.eps: figures/tmpltbank.pdf
	pdftops -eps $^ $@

f5a.eps: figures/bw.pdf
	pdftops -eps $^ $@

f5b.eps: figures/bw_resample.pdf
	pdftops -eps $^ $@

t3.eps: envelope.py
	python $^ $@

# Run 'make publish' to prepare manuscript for submission
ARCHIVENAME = sing$(shell date +%m%d)
@phony: publish
publish: $(ARCHIVENAME).tar.gz
$(ARCHIVENAME).tar.gz: $(PREREQS)
	rm -rf $(ARCHIVENAME)
	mkdir $(ARCHIVENAME)
	ln $(PREREQS) $(ARCHIVENAME)
	tar -chzf $(ARCHIVENAME).tar.gz $(ARCHIVENAME)
	rm -rf $(ARCHIVENAME)

clean:
	rm -f inspiral_svd.{aux,out,log,bbl,blg,pdf} $(FIGURES)
