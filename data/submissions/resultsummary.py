#!/usr/bin/env python3

import glob
import os.path
import json
import sys
from collections import defaultdict


candidates = []

truepos = {}
falsepos = {}
falseneg = {}
correct = {}
incorrect = {}

for d in glob.glob(os.path.join("evaluation","*")):
    if os.path.isdir(d):
        candidate = os.path.basename(d)
        candidates.append(candidate)
        for evalfile in glob.glob(os.path.join(d, "*.json")):
            print("Loading " + evalfile,file=sys.stderr)
            with open(evalfile,'r',encoding='utf-8') as f:
                data = json.load(f)
            for corclass in data.keys():
                print(" - " + corclass,file=sys.stderr)
                if corclass not in truepos: truepos[corclass] = defaultdict(float)
                if corclass not in falsepos: falsepos[corclass] = defaultdict(float)
                if corclass not in falseneg: falseneg[corclass] = defaultdict(float)
                if corclass not in correct: correct[corclass] = defaultdict(float)
                if corclass not in incorrect: incorrect[corclass] = defaultdict(float)
                truepos[corclass][candidate] += data[corclass]['detection']['truepos']
                falseneg[corclass][candidate] += data[corclass]['detection']['falseneg']
                correct[corclass][candidate] += data[corclass]['correction']['correct']
                incorrect[corclass][candidate] += data[corclass]['correction']['incorrect']
                if corclass == 'all':
                    falsepos[corclass][candidate] += data[corclass]['detection']['falsepos']

for candidate in sorted(candidates):
    evaluation = {}
    for corclass in sorted(truepos):
        if candidate in truepos[corclass]:
            evaluation[corclass] = {
                'detection': {
                    'truepos': truepos[corclass][candidate],
                    'falseneg': falseneg[corclass][candidate],
                    'recall': truepos[corclass][candidate] / (truepos[corclass][candidate] + falseneg[corclass][candidate]) if truepos[corclass][candidate]+falseneg[corclass][candidate] else 0.0
                },
                'correction': {
                    'correct': correct[corclass][candidate],
                    'incorrect': incorrect[corclass][candidate],
                    'accuracy': correct[corclass][candidate] / (correct[corclass][candidate] + incorrect[corclass][candidate]) if correct[corclass][candidate]+incorrect[corclass][candidate] else 0.0
                },
                'both': {
                    'recall': correct[corclass][candidate] / (truepos[corclass][candidate] + falseneg[corclass][candidate]) if truepos[corclass][candidate]+falseneg[corclass][candidate] else 0.0
                }
            }
            if corclass == 'all':
                evaluation[corclass]['detection']['falsepos'] = falsepos[corclass][candidate]
                evaluation[corclass]['detection']['precision'] =  truepos[corclass][candidate] / (truepos[corclass][candidate] + falsepos[corclass][candidate]) if truepos[corclass][candidate] + falsepos[corclass][candidate] else 0.0
                evaluation[corclass]['both']['precision'] =  correct[corclass][candidate] / (truepos[corclass][candidate] + falsepos[corclass][candidate]) if truepos[corclass][candidate] + falsepos[corclass][candidate] else 0.0
                if evaluation[corclass]['detection']['precision'] + evaluation[corclass]['detection']['recall'] > 0:
                    evaluation[corclass]['detection']['f1score'] = 2 * ((evaluation[corclass]['detection']['precision'] * evaluation[corclass]['detection']['recall']) / (evaluation[corclass]['detection']['precision'] + evaluation[corclass]['detection']['recall']))
                if evaluation[corclass]['both']['precision'] + evaluation[corclass]['both']['recall'] > 0:
                    evaluation[corclass]['both']['f1score'] = 2 * ((evaluation[corclass]['both']['precision'] * evaluation[corclass]['both']['recall']) / (evaluation[corclass]['both']['precision'] + evaluation[corclass]['both']['recall']))

    with open("results." + str(candidate) + ".json",'w',encoding='utf-8') as f:
        print(json.dumps(evaluation, indent=4), file=f)



