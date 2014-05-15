TEX = env TEXINPUTS=:$(CURDIR)/packages/astronat/apj: pdflatex -file-line-error -halt-on-error -shell-escape
BIBTEX = env BSTINPUTS=:$(CURDIR)/packages/astronat/apj: TEXINPUTS=:$(CURDIR)/packages/astronat/apj: bibtex

FIGURES = \
	figures/snr_in_time.pdf \
	figures/localization_uncertainty.pdf \
	figures/lloid-diagram.pdf \
	figures/upsample-symbol.pdf \
	figures/downsample-symbol.pdf \
	figures/adder-symbol.pdf \
	figures/fir-symbol.pdf \
	figures/tmpltbank.pdf \
	figures/bw.pdf \
	figures/bw_resample.pdf \
	figures/envelope.pdf \
	figures/asds.pdf \
	figures/weighted_asds.pdf \
	figures/accum_snr.pdf \
	figures/inspiral_tf_relation.pdf \
	figures/psd_legend.pdf
PREREQS = \
	$(FIGURES) article.tex macros.tex references.bib

article.pdf: $(PREREQS)
	$(TEX) -draftmode article
	$(BIBTEX) article
	$(TEX) -draftmode article
	$(TEX) article

figures/snr_in_time.pdf: snr_in_time.py matplotlibrc
	python $< $@

figures/localization_uncertainty.pdf: localization_uncertainty.py matplotlibrc
	python $< $@

figures/asds.pdf: plot_asds.py noisemodels.py matplotlibrc
	python $< $@

figures/weighted_asds.pdf: plot_weighted_asds.py noisemodels.py matplotlibrc
	python $< $@

figures/accum_snr.pdf: plot_accum_snr.py noisemodels.py matplotlibrc
	python $< $@

figures/inspiral_tf_relation.pdf: plot_inspiral_tf_relation.py noisemodels.py matplotlibrc
	python $< $@

figures/tmpltbank.pdf: plot_bank.py matplotlibrc
	python $< $@

figures/psd_legend.pdf: plot_legend.py noisemodels.py matplotlibrc
	python $< $@

figures/envelope.pdf: envelope.py matplotlibrc
	python $< $@

article.tar.gz: $(PREREQS) article.bbl
	COPYFILE_DISABLE=true tar -H -czf $@ $^

clean:
	rm -f article.{aux,out,log,bbl,blg,pdf} article.tar.gz $(FIGURES)
