TEX = env TEXINPUTS=:../packages/signalflowlibrary: pdflatex -file-line-error -halt-on-error -shell-escape
FIGURES = lloid-diagram downsample-symbol upsample-symbol adder-symbol fir-symbol

all: $(foreach X,$(FIGURES),$X.eps)

.INTERMEDIATE: diagram.pdf

diagram.pdf: diagram.tex
	$(TEX) diagram

$(foreach X,$(FIGURES),$X.eps): diagram.pdf
	true # noop

clean:
	rm -f $(foreach X,$(FIGURES),$X.{dpth,log,pdf,eps}) diagram.{pdf,aux,auxlock,log}
