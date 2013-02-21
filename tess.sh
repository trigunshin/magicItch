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
    #convert "$hash".png -auto-level -resize 162x91 -compress none "$hash".tiff
    #convert "$hash".png -auto-level -resize 243x137 -compress none "$hash".tiff
    #convert "$hash".png -auto-level -resize 324x182 -compress none "$hash".tiff
    #convert "$hash".png -auto-level -resize 486x273 -compress none "$hash".tiff
    convert "$hash".png -auto-level -resize 648x364 -compress none "$hash".tiff
    #convert "$hash".png -despeckle -threshold 50% -auto-level -resize 638x364 -compress none "$hash".tiff#effective
    #convert "$hash".png -auto-level -resize 837x455 -compress none "$hash".tiff#effective
    #convert "$hash".png -auto-level -resize 1296x728 -compress none "$hash".tiff
    #convert "$hash".png -auto-level -resize 1458x819 -compress none "$hash".tiff
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
