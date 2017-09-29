
import sys
import re

infile = sys.argv[1]
outfile = sys.argv[2]

output = []
pages = 0
parsed = 0
ugly_link_start = re.compile('^\[\[.*')
ugly_link_start2 = re.compile('^\{\{.*')
ugly_link_start3 = re.compile('^\*\{\{.*')
ugly_link_start4 = re.compile('^!.*')
ugly_link_start5 = re.compile('^\{\|.*')
ugly_link_start6 = re.compile('^\* \[\[.*')
ugly_link_start6 = re.compile('^Bestand:')
ugly_link_end = re.compile('.*\]\]$')
ugly_link_end2 = re.compile('.*\}\}$')
ugly_link_end3 = re.compile('.*=$')
pipe_start = re.compile('^\|')
pipe_end = re.compile('.*\|$')
with open(infile,'r',encoding='utf-8') as file_in:
    lines = file_in.read().strip().split('\n')
    gallery = False
    for line in lines:
        l = line.strip()
        if gallery:
            if l == '</gallery>':
                gallery = False
        else:
            if l == '<gallery>':
                gallery = True
            else:
                if not ugly_link_start3.match(l) and not ugly_link_start4.match(l) and not ugly_link_start5.match(l) and not (ugly_link_start.match(l) and ugly_link_end.match(l)) and not (ugly_link_start6.match(l) and ugly_link_end.match(l)) and not (ugly_link_start2.match(l) and ugly_link_end2.match(l)) and not (ugly_link_start2.match(l) and ugly_link_end3.match(l)) and not pipe_start.match(l) and not ugly_link_end2.match(l) and not ugly_link_start2.match(l) and not pipe_end.match(l):
                    if re.search('Afbeelding:',l):
                        try:
                            s = l.split('[[Afbeelding:')
                            l = s[0] + s[1].split(']]',1)[1]
                        except:
                            print('error',l)
                    if re.search('afbeelding:',l):
                        try:
                            s = l.split('[[afbeelding:')
                            l = s[0] + s[1].split(']]',1)[1]
                        except:
                            print('error',l)
                    l = l.replace('<br>','')
                    l = l.replace('<br />','')
                    l = l.replace('<br/>','')
                    l = l.replace('<BR />','')
                    l = l.replace('<BR>','')
                    l = l.replace('<BR/>','')
                    l = l.replace(' | ',' ')
                    output.append(l)

with open(outfile,'w',encoding='utf-8') as file_out:
    file_out.write('\n'.join(output))
