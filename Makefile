###################################################################
# Name of master .tex file for thesis 
manuscript = thesis
bibliography = references

# name of build directory for thesis
bdir = compile

# user-acquired lengths for front and backmatter
front_length = 13
back_length = 9

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
#     make intro
###################################################################
chapter = "\includeonly{chapters/intro/introduction}"

intro:
	mkdir -p $(bdir)
	pdflatex -jobname=int $(latexopt) $(chapter)"\input{thesis}"
	biber $(bdir)/int
	pdflatex -jobname=int $(latexopt) $(chapter)"\input{thesis}"
	pdflatex -jobname=int $(latexopt) $(chapter)"\input{thesis}"
	./pdfsplit.sh $(bdir)/int.pdf 14 16 $(bdir)/intro.pdf 
	rm $(bdir)/int.*

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
