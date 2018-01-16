#!/usr/bin/env python3

import sys
import argparse
import json
from clin28tools.format import CLIN28JSON, ValidationError


def main():
    parser = argparse.ArgumentParser(description="CLIN 28 Evaluation script", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ref', type=str,help="Reference output (JSON)", action='store',required=True)
    parser.add_argument('--out', type=str,help="System output to evaluate (JSON)", action='store',required=True)
    parser.add_argument('--noconfidence', type=str,help="Do not do take into account confidence scores (no weighting)", action='store_true',required=True)
    args = parser.parse_args()

    refdata = CLIN28JSON(args.ref)
    try:
        outdata = CLIN28JSON(args.out)
    except ValidationError:
        print("Attempting to load " + args.out + " in spite of validation error",file=sys.stderr)
        outdata = CLIN28JSON(args.out, validation=False)


    #detection
    truepos = 0.0
    falsepos = 0.0
    falseneg = 0.0
    #correction
    correct = 0.0
    incorrect = 0.0

    for refcorrection in refdata.corrections():
        found = False
        for outcorrection in outdata.corrections():
            if 'span' in refcorrection and 'span' in outcorrection:
                if refcorrection['span'] == outcorrection['span']:
                    outcorrection['found'] = found = True
                    confidence = outcorrection['confidence'] if 'confidence' in outcorrection and not args.noconfidence else 1.0
                    span = True
            elif 'after' in refcorrection and 'after' in outcorrection:
                if refcorrection['after'] == outcorrection['after']:
                    outcorrection['found'] = found = True
                    confidence = outcorrection['confidence'] if 'confidence' in outcorrection and not args.noconfidence else 1.0
                    span = False
            if found: break #no need to look further
        if found:
            truepos += confidence
            if span:
                print("[DETECTION MATCH] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION MATCH] INSERTION AFTER " + refcorrection['after'] + ": " + outcorrection['text'],file=sys.stderr)

            if refcorrection['text'] == outcorrection['text']: #case sensitive!
                correct += confidence
                print("\t[CORRECT]",file=sys.stderr)
            else:
                incorrect += confidence
                print("\t[INCORRECT] Should be: " + refcorrection['text'],file=sys.stderr)
        else:
            falseneg += 1
            if 'span' in refcorrection:
                print("[DETECTION MISS] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]) + " -> " + refcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION MISS] INSERTION AFTER " + refcorrection['after'] + ": " + refcorrection['text'],file=sys.stderr)

    for outcorrection in outdata.corrections():
        if 'found' not in outcorrection:
            confidence = outcorrection['confidence'] if 'confidence' in outcorrection and not args.noconfidence else 1.0
            falsepos += confidence
            if 'span' in outcorrection:
                try:
                    print("[DETECTION WRONG] " + ";".join(outcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in outcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
                except KeyError:
                    print("[DETECTION WRONG AND WORDID MISMATCH] " + ";".join(outcorrection['span']) + ": " + " ".join([ wordid for wordid in outcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION WRONG] INSERTION AFTER " + outcorrection['after'] + ": " + outcorrection['text'],file=sys.stderr)


    evaluation = {
        'detection': {
            'truepos': truepos,
            'falsepos': falsepos,
            'falseneg': falseneg,
            'precision': truepos / (truepos + falsepos) if truepos + falsepos else 0.0,
            'recall': truepos / (truepos + falseneg) if truepos+falseneg else 0.0,
        },
        'correction': {
            'correct': correct,
            'incorrect': incorrect,
            'accuracy': correct / (correct + incorrect) if correct+incorrect else 0.0,
            'precision': correct / (truepos + falsepos) if truepos+falsepos else 0.0,
            'recall': correct / (truepos + falseneg) if truepos+falseneg else 0.0,
        },
    }
    if evaluation['detection']['precision'] + evaluation['detection']['recall'] > 0:
        evaluation['detection']['f1score'] = 2 * ((evaluation['detection']['precision'] * evaluation['detection']['recall']) / (evaluation['detection']['precision'] + evaluation['detection']['recall']))
    if evaluation['correction']['precision'] + evaluation['correction']['recall'] > 0:
        evaluation['correction']['f1score'] = 2 * ((evaluation['correction']['precision'] * evaluation['correction']['recall']) / (evaluation['correction']['precision'] + evaluation['correction']['recall']))

    print(json.dumps(evaluation, indent=4))



if __name__ == '__main__':
    main()
