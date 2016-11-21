# dissertation
PhD dissertation files in Latex, makefiles, and pertinent thesis data. 

The page with thesis formatting guidelines:
http://grad.berkeley.edu/academic-progress/thesis/

I got the basic .cls file and latex documents from here:
https://math.berkeley.edu/~vojta/tex/ucbthesis-phd.html

I've committed a general Makefile that will auto compile various things related
to this thesis. To keep things clean, I put all of the extra files created by
latex in a folder called compile. 
* `Make clean` will delete all of the old .aux files.
* `Make all` will build the thesis in its entirety. 

In progress:
* `Make chaptername` will build a specific chapter without all of the other
  stuff in the thesis. 
* `Make outline` will generate just a table of contents for the thesis

