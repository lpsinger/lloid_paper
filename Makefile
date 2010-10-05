TEX = echo X | pdflatex

PREREQS = \
	inspiral_svd.tex

inspiral_svd.pdf: $(PREREQS)
	$(TEX) inspiral_svd && $(TEX) inspiral_svd && bibtex inspiral_svd && $(TEX) inspiral_svd

clean:
	rm -f inspiral_svd.{aux,log,pdf}