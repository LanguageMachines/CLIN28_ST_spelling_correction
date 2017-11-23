#!/usr/bin/env python3

import sys
import argparse
import json
from clin28tools.format import CLIN28JSON


def main():
    parser = argparse.ArgumentParser(description="CLIN 28 Evaluation script", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ref', type=str,help="Reference output (JSON)", action='store',required=True)
    parser.add_argument('--out', type=str,help="System output to evaluate (JSON)", action='store',required=True)
    args = parser.parse_args()

    refdata = CLIN28JSON(args.ref)
    outdata = CLIN28JSON(args.out)


    #detection
    truepos = 0
    falsepos = 0
    falseneg = 0
    #correction
    correct = 0
    incorrect = 0

    for refcorrection in refdata.corrections():
        found = False
        for outcorrection in outdata.corrections():
            if 'span' in refcorrection and 'span' in outcorrection:
                if refcorrection['span'] == outcorrection['span']:
                    outcorrection['found'] = found = True
                    span = True
            elif 'after' in refcorrection and 'after' in outcorrection:
                if refcorrection['after'] == outcorrection['after']:
                    outcorrection['found'] = found = True
                    span = False
            if found: break #no need to look further
        if found:
            truepos += 1
            if span:
                print("[DETECTION MATCH] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION MATCH] INSERTION AFTER " + refcorrection['after'] + ": " + outcorrection['text'],file=sys.stderr)

            if refcorrection['text'] == outcorrection['text']: #case sensitive!
                correct += 1
                print("\t[CORRECT]",file=sys.stderr)
            else:
                incorrect += 1
                print("\t[INCORRECT] Should be: " + refcorrection['text'],file=sys.stderr)
        else:
            falseneg += 1
            if span:
                print("[DETECTION MISS] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]) + " -> " + refcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION MISS] INSERTION AFTER " + refcorrection['after'] + ": " + refcorrection['text'],file=sys.stderr)

    for outcorrection in outdata.corrections():
        if 'found' not in outcorrection:
            falsepos += 1
            if span:
                print("[DETECTION WRONG] " + ";".join(outcorrection['span']) + ": " + " ".join([ outdata[wordid]['text'] for wordid in outcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION WRONG] INSERTION AFTER " + outcorrection['after'] + ": " + outcorrection['text'],file=sys.stderr)


    evaluation = {
        'detection': {
            'truepos': truepos,
            'falsepos': falsepos,
            'falseneg': falseneg,
            'precision': truepos / (truepos + falsepos),
            'recall': truepos / (truepos + falseneg),
        },
        'correction': {
            'correct': correct,
            'incorrect': incorrect,
            'precision': correct / (truepos + falsepos),
            'recall': correct / (truepos + falseneg),
        },
    }
    evaluation['detection']['f1score'] = 2 * ((evaluation['detection']['precision'] * evaluation['detection']['recall']) / (evaluation['detection']['precision'] + evaluation['detection']['recall']))
    evaluation['correction']['f1score'] = 2 * ((evaluation['correction']['precision'] * evaluation['correction']['recall']) / (evaluation['correction']['precision'] + evaluation['correction']['recall']))

    print(json.dumps(evaluation, indent=4))



if __name__ == '__main__':
    main()
