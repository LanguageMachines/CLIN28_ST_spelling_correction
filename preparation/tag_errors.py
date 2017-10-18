

import sys
import copy

from pynlpl.formats import folia

infile = sys.argv[1]
outfile = sys.argv[2]

doc = folia.Document(file=infile)
doc.declare(folia.Observation,set='https://raw.githubusercontent.com/proycon/folia/master/setdefinitions/spellingcorrection.foliaset.xml')

error = False
errorseg = []
to_remove = False
while True:
    br = True
    for word in doc.words():
        if error:
            if word.text() == 'FOUTJE': # tag errorseg
                error = False
                word.parent.remove(word) # remove word
                to_remove.parent.remove(to_remove)
                to_remove = False
                if len(errorseg) > 0:
                    errorseg[0].add(folia.Observation,*errorseg,cls='uncertain')
                    errorseg = []
                br = False
                break
            else:
                errorseg.append(word)
        else:
            if word.text() == 'FOUTJE':
                error = True
                to_remove = word
    if br:
        break

doc.save(outfile)
