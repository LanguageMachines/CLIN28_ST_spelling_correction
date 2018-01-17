#!/usr/bin/env python3

import sys
import argparse
import json
from collections import defaultdict
from clin28tools.format import CLIN28JSON, ValidationError


def main():
    parser = argparse.ArgumentParser(description="CLIN 28 Evaluation script", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--ref', type=str,help="Reference output (JSON)", action='store',required=True)
    parser.add_argument('--out', type=str,help="System output to evaluate (JSON)", action='store',required=True)
    parser.add_argument('--noconfidence', help="Do not do take into account confidence scores (no weighting)", action='store_true', default=False)
    parser.add_argument('--withnumbers', help="Do not skip corrections on numbers", action='store_true', default=False)
    parser.add_argument('--ignoreclasses', type=str,help="Correction classes to ignore (comma-separated list)", action='store', default=False)
    args = parser.parse_args()

    refdata = CLIN28JSON(args.ref)
    try:
        outdata = CLIN28JSON(args.out)
    except ValidationError:
        print("Attempting to load " + args.out + " in spite of validation error",file=sys.stderr)
        outdata = CLIN28JSON(args.out, validation=False)


    #detection
    truepos = defaultdict(float)
    falsepos = 0.0
    falseneg = defaultdict(float)
    #correction
    correct = defaultdict(float)
    incorrect = defaultdict(float)

    classes = set()

    for refcorrection in refdata.corrections():
        found = False
        if  not args.withnumbers and (refcorrection['text'].isdigit() or ('span' in refcorrection and " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]).isdigit())):
            skip = True
        elif args.ignoreclasses and refcorrection['class'] in args.ignoreclasses.split(','):
            skip = True
        else:
            skip = False
            for corclass in ('all',refcorrection['class']):
                classes.add(corclass)

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

        if not skip:
            if found:
                for corclass in ('all',refcorrection['class']):
                    truepos[corclass] += 1
                if span:
                    print("[DETECTION MATCH] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
                else:
                    print("[DETECTION MATCH] INSERTION AFTER " + refcorrection['after'] + ": " + outcorrection['text'],file=sys.stderr)

                if refcorrection['text'] == outcorrection['text']: #case sensitive!
                    for corclass in ('all',refcorrection['class']):
                        correct[corclass] += confidence
                    print("\t[CORRECT]",file=sys.stderr)
                else:
                    for corclass in ('all',refcorrection['class']):
                        incorrect[corclass] += confidence
                    print("\t[INCORRECT] Should be: " + refcorrection['text'],file=sys.stderr)
            else:
                for corclass in ('all',refcorrection['class']):
                    falseneg[corclass] += 1
                if 'span' in refcorrection:
                    print("[DETECTION MISS] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]) + " -> " + refcorrection['text'],file=sys.stderr)
                else:
                    print("[DETECTION MISS] INSERTION AFTER " + refcorrection['after'] + ": " + refcorrection['text'],file=sys.stderr)
        elif found: #skip and found
            print("[SKIPPED] " + ";".join(refcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in refcorrection['span'] ]),file=sys.stderr)

    for outcorrection in outdata.corrections():
        if 'found' not in outcorrection:
            confidence = outcorrection['confidence'] if 'confidence' in outcorrection and not args.noconfidence else 1.0
            falsepos += 1
            if 'span' in outcorrection:
                try:
                    print("[DETECTION WRONG] " + ";".join(outcorrection['span']) + ": " + " ".join([ refdata[wordid]['text'] for wordid in outcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
                except KeyError:
                    print("[DETECTION WRONG AND WORDID MISMATCH] " + ";".join(outcorrection['span']) + ": " + " ".join([ wordid for wordid in outcorrection['span'] ]) + " -> " + outcorrection['text'],file=sys.stderr)
            else:
                print("[DETECTION WRONG] INSERTION AFTER " + outcorrection['after'] + ": " + outcorrection['text'],file=sys.stderr)

    evaluation = {}
    for corclass in sorted(classes):
        evaluation[corclass] = {
            'detection': {
                'truepos': truepos[corclass],
                'falseneg': falseneg[corclass],
                'recall': truepos[corclass] / (truepos[corclass] + falseneg[corclass]) if truepos[corclass]+falseneg[corclass] else 0.0
            },
            'correction': {
                'correct': correct[corclass],
                'incorrect': incorrect[corclass],
                'accuracy': correct[corclass] / (correct[corclass] + incorrect[corclass]) if correct[corclass]+incorrect[corclass] else 0.0
            },
            'both': {
                'recall': correct[corclass] / (truepos[corclass] + falseneg[corclass]) if truepos[corclass]+falseneg[corclass] else 0.0
            }
        }
        if corclass == 'all':
            evaluation[corclass]['detection']['falsepos'] = falsepos
            evaluation[corclass]['detection']['precision'] =  truepos[corclass] / (truepos[corclass] + falsepos) if truepos[corclass] + falsepos else 0.0
            evaluation[corclass]['both']['precision'] =  correct[corclass] / (truepos[corclass] + falsepos) if truepos[corclass] + falsepos else 0.0
            if evaluation[corclass]['detection']['precision'] + evaluation[corclass]['detection']['recall'] > 0:
                evaluation[corclass]['detection']['f1score'] = 2 * ((evaluation[corclass]['detection']['precision'] * evaluation[corclass]['detection']['recall']) / (evaluation[corclass]['detection']['precision'] + evaluation[corclass]['detection']['recall']))
            if evaluation[corclass]['both']['precision'] + evaluation[corclass]['both']['recall'] > 0:
                evaluation[corclass]['both']['f1score'] = 2 * ((evaluation[corclass]['both']['precision'] * evaluation[corclass]['both']['recall']) / (evaluation[corclass]['both']['precision'] + evaluation[corclass]['both']['recall']))

    print(json.dumps(evaluation, indent=4))



if __name__ == '__main__':
    main()
