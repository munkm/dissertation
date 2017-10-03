# dissertation
PhD dissertation files in Latex, makefiles, and pertinent thesis data. 

The page with thesis formatting guidelines:
http://grad.berkeley.edu/academic-progress/thesis/

I got the basic .cls file and latex documents from here:
https://math.berkeley.edu/~vojta/tex/ucbthesis-phd.html

I've committed a general Makefile that will auto compile various things related
to this thesis. To keep things clean, I put all of the extra files created by
latex in a folder called `./compile/`. 
* `Make clean` will delete all of the old .aux files.
* `Make all` will build the thesis in its entirety.


Other makefile options:
* `Make intro` will make the introduction chapter. This is also available with
  all of the main body chapters in the dissertation. I have not modified the
  makefile to only make the appendices
  * **Requirements**: 
    * **ghostscript** -- the `pdfsplit.sh` file uses ghostscript to 
    separate out the body of the chapter from the front and back matter of the
    dissertation. You can see if you have ghostscript by entering `which gs` on
    the command line.
    * **pdfinfo** -- this tool i use to get the page count of the intermediate pdf
    created in the chapter generation. Without this tool you'll have to more
    extensively modify the makefile to separate out the chapter from the
    front and back matter. 
    * setting `front_length` and `back_length` variables in the Makefile.
    Because each dissertation will vary in the length of their bibliography
    and frontmatter pagination, these are hard set in the Makefile. You'll
    have to have knowledge of the pagination of each of these sections, and
    they'll be used to compute the page range of the chapter once the
    intermediate pdf is created. 

In progress:
* `Make outline` will generate just a table of contents for the thesis

