#!/bin/bash
# this function uses 3 arguments:
#     $1 is the input file name
#     $2 is the first page of the range to extract
#     $3 is the last page of the range to extract
#     $4 is the output file name
#     output file will be named "inputfile_pXX-pYY.pdf"
gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER \
   -dFirstPage=${2} \
   -dLastPage=${3} \
   -sOutputFile=${4} \
   ${1}
