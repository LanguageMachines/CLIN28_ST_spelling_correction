
import sys
from bs4 import BeautifulSoup
import json
import difflib
import re

infile = sys.argv[1]
outfile = sys.argv[2]

def return_tagtext(s,t):
    c = [x for x in s.findAll(t)]
    if len(c) > 0:
        return c[0]
    else:
        return False

def is_sp(comment):
    if comment.text[:2] == 'sp':
        return True
    else:
        return False

def diff_txts(t1,t2):
    diffs = []
    s = difflib.SequenceMatcher(None, t1, t2)
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag != 'equal':
            d = [tag, i1, i2, t1[i1:i2], j1, j2, t2[j1:j2]]
            diffs.append(d)

    # for l,s in enumerate(difflib.ndiff(t1, t2)):
    #     if s[0]==' ': continue
    #     elif s[0]=='-':
    #         diff = {'position':l,'type':'-','20_char_window_before':t1[(l-10):(l+10)],'20_char_window_after':t2[(l-10):(l+10)]}
    #         diffs.append(diff)
    #     elif s[0] == '+':
    #         diff = {'position':l,'type':'+','20_char_window_before':t1[(l-10):(l+10)],'20_char_window_after':t2[(l-10):(l+10)]}
    #         diffs.append(diff)
    return diffs

def parse_page(page):
    title = return_tagtext(page,'title').text
    spelling_revisions = []
    for i,r in enumerate(page.findAll('revision')):        
        c = return_tagtext(r,'comment')
        if c:
            if is_sp(c):
                t1 = return_tagtext(page.findAll('revision')[i-1],'text').text                    
                t2 = return_tagtext(r,'text').text                
                diffs = diff_txts(t1,t2)
                for diff in reversed(diffs):
                    try:
                        error_position_start = diff[1]
                        ch = t1[error_position_start]
                    except:
                        continue
                    while ch != ' ' and ch != '!' and ch != '?' and ch != '.':
                        error_position_start -= 1
                        try:
                            ch = t1[error_position_start]
                        except:
                            break
                    error_position_end = diff[2]
                    try:
                        ch = t1[error_position_end]
                    except:
                        error_position_end -= 1
                        ch = t1[error_position_end]
                    while ch != ' ' and ch != '!' and ch != '?' and ch != '.':
                        error_position_end += 1
                        try:
                            ch = t1[error_position_end]
                        except:
                            break
                    t1 = t1[:error_position_start] + ' FOUTJE' + t1[error_position_start:error_position_end] + ' FOUTJE' + t1[error_position_end:]
                spelling_revisions.append(t1)
    if len(spelling_revisions) > 0:
        # return '<page>\n<title>' + title + '</title>\n' + '\n'.join(spelling_revisions) + '\n</page>'
        return spelling_revisions
    else:
        return False 


output = []
pages = 0
parsed = 0
ugly_link_start = re.compile('^\[\[.+')
ugly_link_start2 = re.compile('^<.+')
ugly_link_end = re.compile('.+\]\]$')
pipe_start = re.compile('^\|')
with open(infile,'r',encoding='utf-8') as file_in:
    p = False  
    # for line in file_in.readlines():
    for line in file_in:
        if line.strip() == '<page>':
            p = line
        elif line.strip() == '</page>':
            p += line
            souped = BeautifulSoup(p, 'html.parser')
            page_parsed = parse_page(souped)
            if page_parsed:
                for pp in page_parsed:
                    parsed += 1
                    print('PARSED',parsed,'PAGES')
                    with open(outfile + 'page' + str(parsed) + '.mediawiki','w',encoding='utf-8') as out:
                        out.write(pp)
                    if parsed == 1000:
                        quit()
            pages += 1
            print('processed',pages,'pages')
        else:
            if p:
                # l = line.strip()
                # if not (ugly_link_start.match(l) and ugly_link_end.match(l)) and not pipe_start.match(line.strip()):
                p += line
