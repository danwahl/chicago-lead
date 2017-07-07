import slate
import re
import os

if __name__ == '__main__':
    # pattern for finding cross street
    ps = re.compile(r'(?:.*?)?\sin\s(.*?),\sfrom\s(.*?)\sto\s(.*?)(?<![A-Z])[,\.]')
    
    # pattern for finding job id
    pj = re.compile(r'\D(\d{7})\D')
    
    # pattern for finding date
    
    for subdir, dirs, files in os.walk('dwm data'):
        for n in files:
            with open(os.path.join(subdir, n)) as f:
                print n
                
                # read pdf
                doc = slate.PDF(f)
                
                # find job number
                j = pj.findall(doc[0])
                print j
                
                # find date
                
                
                # split first page by paragraphs
                page = doc[0].split('\n\n \n\n')
                
                # iterate through paragraphs
                for line in page:
                    # clean remaining line breaks
                    text = line.replace('\n','').decode('unicode_escape').encode('ascii','ignore')
                    #print text
                    
                    # find matches
                    ms = ps.findall(text)  
                    for m in ms:
                        print 'Match found: ', len(m), m
        

