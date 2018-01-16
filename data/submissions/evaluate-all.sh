#!/bin/bash

for d in ?/; do
    for f in $d/*.json; do
        nr=$(basename $d)
        filename=$(basename $f)
        mkdir -p evaluation/$nr 2>/dev/null
        clin28-evaluate --out $f --ref ../goldstandard/$filename > evaluation/$nr/$filename 2>evaluation/$nr/${filename/json/log}
    done
done

python3 resultsummary.py

