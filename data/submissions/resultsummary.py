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
truepos_correction = {}
falseneg_correction = {}

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
                truepos_correction[corclass][candidate] += data[corclass]['correction']['truepos_correction']
                falseneg_correction[corclass][candidate] += data[corclass]['correction']['falseneg_correction']
                if corclass == 'all':
                    falsepos[corclass][candidate] += data[corclass]['detection']['falsepos'] #correction falsepos is the same by definiton

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
                    'truepos': truepos_correction[corclass][candidate],
                    'falseneg': falseneg_correction[corclass][candidate],
                    'recall': truepos_correction[corclass][candidate] / (truepos_correction[corclass][candidate] + falseneg_correction[corclass][candidate]) if truepos_correction[corclass][candidate]+falseneg_correction[corclass][candidate] else 0.0
                }
            }
            if corclass == 'all':
                evaluation[corclass]['detection']['falsepos'] = falsepos[corclass][candidate]
                evaluation[corclass]['correction']['falsepos'] = falsepos[corclass][candidate]
                evaluation[corclass]['detection']['precision'] =  truepos[corclass][candidate] / (truepos[corclass][candidate] + falsepos[corclass][candidate]) if truepos[corclass][candidate] + falsepos[corclass][candidate] else 0.0
                evaluation[corclass]['correction']['precision'] =  truepos_correction[corclass][candidate] / (truepos_correction[corclass][candidate] + falsepos[corclass][candidate]) if truepos_correction[corclass][candidate] + falsepos[corclass][candidate] else 0.0
                if evaluation[corclass]['detection']['precision'] + evaluation[corclass]['detection']['recall'] > 0:
                    evaluation[corclass]['detection']['f1score'] = 2 * ((evaluation[corclass]['detection']['precision'] * evaluation[corclass]['detection']['recall']) / (evaluation[corclass]['detection']['precision'] + evaluation[corclass]['detection']['recall']))
                if evaluation[corclass]['correction']['precision'] + evaluation[corclass]['correction']['recall'] > 0:
                    evaluation[corclass]['correction']['f1score'] = 2 * ((evaluation[corclass]['correction']['precision'] * evaluation[corclass]['correction']['recall']) / (evaluation[corclass]['correction']['precision'] + evaluation[corclass]['correction']['recall']))

    with open("results." + str(candidate) + ".json",'w',encoding='utf-8') as f:
        print(json.dumps(evaluation, indent=4), file=f)



