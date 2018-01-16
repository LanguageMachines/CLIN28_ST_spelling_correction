#!/usr/bin/env python3

import glob
import os.path
import json
import sys
from collections import defaultdict

truepos = defaultdict(int)
falsepos = defaultdict(int)
falseneg = defaultdict(int)
correct = defaultdict(int)
incorrect = defaultdict(int)

candidates = []

for d in glob.glob(os.path.join("evaluation","*")):
    if os.path.isdir(d):
        candidate = os.path.basename(d)
        candidates.append(candidate)
        for evalfile in glob.glob(os.path.join(d, "*.json")):
            print("Loading " + evalfile,file=sys.stderr)
            with open(evalfile,'r',encoding='utf-8') as f:
                data = json.load(f)
            truepos[candidate] += data['detection']['truepos']
            falsepos[candidate] += data['detection']['falsepos']
            falseneg[candidate] += data['detection']['falseneg']
            correct[candidate] += data['correction']['correct']
            incorrect[candidate] += data['correction']['incorrect']

for candidate in sorted(candidates):
    evaluation = {
        'candidate': candidate,
        'detection': {
            'truepos': truepos[candidate],
            'falsepos': falsepos[candidate],
            'falseneg': falseneg[candidate],
            'precision': truepos[candidate] / (truepos[candidate] + falsepos[candidate]) if truepos[candidate] + falsepos[candidate] else 0.0,
            'recall': truepos[candidate] / (truepos[candidate] + falseneg[candidate]) if truepos[candidate]+falseneg[candidate] else 0.0,
        },
        'correction': {
            'correct': correct[candidate],
            'incorrect': incorrect[candidate],
            'accuracy': correct[candidate] / (correct[candidate] + incorrect[candidate]) if correct[candidate]+incorrect[candidate] else 0.0,
            'precision': correct[candidate] / (truepos[candidate] + falsepos[candidate]) if truepos[candidate]+falsepos[candidate] else 0.0,
            'recall': correct[candidate] / (truepos[candidate] + falseneg[candidate]) if truepos[candidate]+falseneg[candidate] else 0.0,
        },
    }
    if evaluation['detection']['precision'] + evaluation['detection']['recall'] > 0:
        evaluation['detection']['f1score'] = 2 * ((evaluation['detection']['precision'] * evaluation['detection']['recall']) / (evaluation['detection']['precision'] + evaluation['detection']['recall']))
    if evaluation['correction']['precision'] + evaluation['correction']['recall'] > 0:
        evaluation['correction']['f1score'] = 2 * ((evaluation['correction']['precision'] * evaluation['correction']['recall']) / (evaluation['correction']['precision'] + evaluation['correction']['recall']))
    print(json.dumps(evaluation, indent=4))



