#!/usr/bin/env python3

import sys
import argparse
import json
from pynlpl.formats import folia


def all_original_words(doc):
    for word in doc.select(folia.Word,ignore=False): #really iterate over all words, not just the authoritative ones
        if not any( isinstance(ancestor, (folia.New, folia.Current)) for ancestor in word.ancestors() ): #exclude words that are part of a structural correction
            yield word

def folia2json(doc, docorrections=True):
    words = []
    corrections = []
    for word in all_original_words(doc):
        words.append({'id':word.id, 'text': word.text(correctionhandling=folia.CorrectionHandling.ORIGINAL), 'space': word.space, 'in':word.ancestor(folia.AbstractStructureElement).id})
    if docorrections:
        for correction in doc.select(folia.Correction):
            structural =  not any( isinstance(ancestor, folia.Word) for ancestor in correction.ancestors() ) #is the correction confined to a single word/token or is it structural?
            print("correction ", correction.id, "structural=", structural,file=sys.stderr)
            if structural:
                span = []
                try:
                    for origword in correction.original().select(folia.Word,ignore=False):
                        span.append(origword.id)
                except folia.NoSuchAnnotation:
                    pass
                if not span:
                    #we have an insertion
                    previous = correction.previous(folia.Word).id
            else:
                span = [correction.parent.id]
            try:
                text = correction.text()
            except folia.NoSuchText:
                #deletion
                text = ""
            if span:
                corrections.append({'class': correction.cls, 'span': span,'text':text })
            else:
                corrections.append({'class': correction.cls, 'after': previous,'text':text })
    return {'words':words, 'corrections': corrections}

def main():
    parser = argparse.ArgumentParser(description="Convert FoLiA to JSON Shared Task format", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-C',dest='corrections',help="Strip corrections", action='store_false',default=True)
    parser.add_argument('file', nargs=1, help='FoLiA Document (input)')
    args = parser.parse_args()

    doc = folia.Document(file=args.file[0])
    data = folia2json(doc, args.corrections)
    print(json.dumps(data, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    main()





