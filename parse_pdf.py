import slate
import re
import os
import sys

if __name__ == '__main__':
    for subdir, dirs, files in os.walk('25th-ward'):
        for n in files:
            # check for pdf
            ext = os.path.splitext(n)[-1].lower()
            if ext != '.pdf':
                continue
             
            with open(os.path.join(subdir, n), 'rb') as f:
                print n
                
                # read pdf, check for water main
                doc = slate.PDF(f)
                if doc[0].find('water main') == -1:
                    print 'sewer'
                    continue
    
    '''
    # pattern for finding cross street
    ps = re.compile(r'(?:.*?)?\s(?:\band\b|\bin\b)\s(.*?),\sfrom\s(.*?)\sto\s(.*?)(?:(?<![A-Z])[,\.]|(?:\s))')
    
    # pattern for finding job id
    pj = re.compile(r'\D(\d{7})\D')
    
    # pattern for finding date
    
    for subdir, dirs, files in os.walk('dwm data'):
        for n in files:
            # check for pdf
            ext = os.path.splitext(n)[-1].lower()
            if ext != '.pdf':
                continue
             
            #with open(os.path.join(subdir, n), 'rb') as f:
            with open(os.path.join('dwm data\\foia\\2015\\01 jan', '20150114_Harrison_Wabash_02w.pdf'), 'rb') as f:
                #print n
                
                # read pdf, check for water main
                doc = slate.PDF(f)
                if doc[0].find('water main') == -1:
                    print 'sewer'
                    continue
                
                # find job number
                j = pj.findall(doc[0])
                print j
                
                # find date
                
                
                # split first page by paragraphs
                page = doc[0].split('\n \n')
                
                # iterate through paragraphs
                for line in page:
                    # clean remaining line breaks
                    text = line.replace('\n','').decode('unicode_escape').encode('ascii','ignore')
                    #print text
                    
                    # find matches
                    ms = ps.findall(text)  
                    for m in ms:
                        print 'Match found: ', len(m), m
                
                sys.exit()
    '''
        

