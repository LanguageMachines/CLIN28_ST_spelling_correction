#!/bin/bash

for f in ../goldstandard/*.json; do
    filename=$(basename $f)
    echo "Evaluating $filename">&2
    for d in ?/; do
        if [ -f $d/$filename ]; then
            nr=$(basename $d)
            echo $nr>&2
            mkdir -p evaluation/$nr 2>/dev/null
            clin28-evaluate --noconfidence --out $d/$filename --ref ../goldstandard/$filename > evaluation/$nr/$filename 2>evaluation/$nr/${filename/json/log}
            if [ $? -ne 0 ]; then
                echo "Failed, check: evaluation/$nr/${filename/json/log}">&2
                exit 2
            fi
        else
            echo "MISSING OUTPUT FOR CANDIDATE $nr: $filename">&2
            exit 2
        fi
    done
done

echo "Computing result summary...">&2
python3 resultsummary.py

