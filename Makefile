###################################################################
# Name of master .tex file for thesis 
manuscript = thesis
# Ch1 = "\includeonly{lit_review}\input{thesis}"
Ch1a = "\includeonly{chapters/lit_review/$(Ch1)}\input{$(manuscript)}"
Ch1 = lit_review
outline = outline
# \input{chapters/methodology/methodology}
# \input{chapters/characterization_tests/char_tests}
# \input{chapters/scaling_tests/scale_tests}
# \input{chapters/conclusions/conclusions}
# Name of master .bib file for bibliography
bibliography = references

# name of build directory for thesis
bdir = compile

# compilation options
latexopt = -halt-on-error -file-line-error -output-directory=$(bdir)
latexopt2 = -halt-on-error -file-line-error -output-directory=$(bdir)/chaptershit

###################################################################
#     make all
###################################################################

all: $(manuscript).pdf

$(manuscript).pdf: $(manuscript).tex $(bibliography).bib
	mkdir -p $(bdir)
	pdflatex $(latexopt) $(manuscript)
	biber    $(bdir)/$(manuscript)
	pdflatex $(latexopt) $(manuscript)
	pdflatex $(latexopt) $(manuscript)


#	biber -terse $(bdir)/$(manuscript)
###################################################################
#     make lit_review
###################################################################

lit_review: $(Ch1).pdf
# lit_review:

$(Ch1).pdf: $(manuscript).tex $(bibliography).bib
	mkdir -p $(bdir)/chaptershit
	pdflatex $(latexopt2) $(Ch1a)
	biber    $(bdir)/chaptershit/$(manuscript)
	pdflatex $(latexopt2) $(Ch1a)
	pdflatex $(latexopt2) $(Ch1a)
	mv ./$(bdir)/chaptershit/$(manuscript).pdf ./$(bdir)/$(Ch1).pdf


###################################################################
#     make outline
###################################################################

outline: $(outline).pdf

$(outline).pdf: $(outline).tex
	latex $(latexopt) $(outline)

###################################################################
#     make clean
###################################################################

clean:
	rm -fr $(bdir)
	find . -name "*.aux" -delete 

.PHONY: all clean
