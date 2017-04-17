import requests
import bs4
import urllib
import os
import time

def get_soup(url):
    page = requests.get(url)
    if page.status_code == 200:
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        return soup

if __name__ == '__main__':
    s3 = get_soup('https://www.cityofchicago.org/city/en/depts/water/supp_info/archived_constructionreports/2009.html')
#    for a1 in s1.select('h3 a'):
#        s2 = get_soup(a1['href'])
#        for a2 in s2.select('h3 a'):
#            s3 = get_soup('https://www.cityofchicago.org/' + a2['href'])
    for d3 in s3.select('div#content-content'):
        for a3 in d3.find_all('a', href=True):
            #path = a1.contents[0].strip() + '\\' + a2.contents[0].strip()
            path = '2009'
            if not os.path.exists(path):
                os.makedirs(path)
            f = os.path.join(path, a3['href'].split('/')[-1]) 
            if not os.path.exists(f):
                while True:
                    try:
                        urllib.urlretrieve('https://www.cityofchicago.org/' + a3['href'], f)
                    except:
                        print 'error, trying again ' + a3['href'] 
                    else:
                        break
                    time.sleep(1)
    
    
    
    
    
    
    
    '''
    page = requests.get('https://www.cityofchicago.org/city/en/depts/water/supp_info/dwm_constructionprojects.html')
    if page.status_code == 200:
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        for a1 in soup.select('h3 a'):
            page = requests.get(a1.attrs['href'])
            soup = bs4.BeautifulSoup(page.content, 'html.parser')
            for a2 in soup.select('h3 a'):
                page = requests.get(a2.attrs['href'])
                soup = bs4.BeautifulSoup(page.content, 'html.parser')
                break
    '''