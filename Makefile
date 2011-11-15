TEX = env TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj: pdflatex -file-line-error -halt-on-error -shell-escape
BIBTEX = env BSTINPUTS=:$(CURDIR)/packages/astronat/apj: TEXINPUTS=:$(CURDIR)/packages/aastex52:$(CURDIR)/packages/astronat/apj: bibtex

FIGURES = f1.eps f2.eps f3.eps f3a.eps f3b.eps f3c.eps f3d.eps f4.eps f5a.eps f5b.eps t3.eps
PREREQS = \
	$(FIGURES) article.tex references.bib

article.pdf: $(PREREQS)
	$(TEX) -draftmode article
	$(BIBTEX) article
	$(TEX) -draftmode article
	$(TEX) article

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
$(ARCHIVENAME).tar.gz: $(PREREQS) readme.txt coverletter.txt article.bbl
	rm -rf $(ARCHIVENAME)
	mkdir $(ARCHIVENAME)
	ln $(FIGURES) article.tex readme.txt coverletter.txt article.bbl $(ARCHIVENAME)
	env COPYFILE_DISABLE=true COPY_EXTENDED_ATTRIBUTES_DISABLE=true tar -chzf $(ARCHIVENAME).tar.gz $(ARCHIVENAME)
	rm -rf $(ARCHIVENAME)

clean:
	rm -f article.{aux,out,log,bbl,blg,pdf} $(FIGURES)
