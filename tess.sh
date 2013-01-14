#!/bin/bash
# Usage: remove all utility bills pdf file password 
shopt -s nullglob
DIR=$1
#echo "using $DIR as directory"
#echo $1
cd $1
for ff in *.png
do
    f=$(basename $ff)
    hash=${f%.*}
    #echo "using $hash for name"
    convert "$hash".png -auto-level -resize 324x182 -compress none "$hash".tiff
    #tesseract creates a $hash.txt output file
    tesseract "$hash".tiff "$hash" mitch 1>/dev/null 2>&1
    #sed -n '2{p;q;}' "$hash.txt" > "$hash"_tmp
    #mv "$hash"_tmp "$hash".txt
    rm "$hash".tiff
    TEXT=`cat $hash.txt | paste -s -d '|'`
    TEXT="$TEXT$hash"
    echo $TEXT
    echo $TEXT >>$hash.txt
    #mv "$hash.png" "done"
    #rm "$hash.txt"
done
