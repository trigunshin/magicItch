#!/bin/bash
#scg_data/scg_2013-02-09.tsv
shopt -s nullglob
for file in scg_data/*
do
    #whatever you need with "$file"
    #loc="$file"
    my_date="${file:13:10}"
    #echo "$file" " " "$my_date"
    python src/mongoExport.py -f "$file" -n '' -d "$my_date" >> bulk.log
done

exit
