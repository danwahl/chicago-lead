import httplib2
from apiclient import discovery, errors
import quickstart
import base64
import bs4
import requests
import time
import re
import geocoder
import gmplot

def ListMessagesWithLabels(service, user_id, query='', label_ids=[]):
    try:
        response = service.users().messages().list(userId=user_id, q=query, labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
          messages.extend(response['messages'])
        
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query, labelIds=label_ids, pageToken=page_token).execute()
            messages.extend(response['messages'])
        
        return messages
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def GetMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        #print 'Message snippet: %s' % message['snippet']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def ModifyMessage(service, user_id, msg_id, msg_labels):
    try:
        message = service.users().messages().modify(userId=user_id, id=msg_id, body=msg_labels).execute()
        
        label_ids = message['labelIds']
        
        print 'Message ID: %s - With Label IDs %s' % (msg_id, label_ids)
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def get_soup(msg):
    html = base64.urlsafe_b64decode(msg['payload']['body']['data'].encode('ASCII'))
    return bs4.BeautifulSoup(html, "html.parser")      

if __name__ == '__main__':
    credentials = quickstart.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    
    # using inbox label to keep track of progress
    msg_labels = {'removeLabelIds': ['INBOX', 'UNREAD'], 'addLabelIds': []}
    
    # pattern for finding cross street
    p = re.compile('\sON\s(.*)\sFROM\s(.*)\sTO\s(.*)')
    
    gmap = gmplot.GoogleMapPlotter(41.8781, -87.6298, 12)
    
    # Registration Confirmation
    reg_msgs = ListMessagesWithLabels(service, 'me', 'Registration Confirmation', ['INBOX'])
    for message in reg_msgs:
        # get message info
        msg = GetMessage(service, 'me', message['id'])
        #print msg['id']
        
        # find the registration confirmation link
        soup = get_soup(msg)       
        link = soup.find_all('a')[0]['href']
        #print link
    
        # open link, remove labels if successful
        response = requests.get(link)
        if response == 200:
            ModifyMessage(service, 'me', message['id'], msg_labels)
        
        time.sleep(1)
    
    # Project Update
    update_msgs = ListMessagesWithLabels(service, 'me', 'Project Update', ['INBOX'])
    for message in update_msgs:
        # get message info
        msg = GetMessage(service, 'me', message['id'])
        dt = msg['internalDate']
        #print msg['id']
        
        for header in msg['payload']['headers']:
            if header['name'] == 'Subject':
                job_id = re.findall('\d+', header['value'])[0]
        
        # find the job code
        soup = get_soup(msg)
        job_id = int(soup.find_all('span')[0].contents[0])
        
        # find cross streets
        segments = soup.find_all('li')
        for s in segments:
            m = p.match(s.contents[0])  
            if m:
                print 'Match found: ', m.groups()
                
                lats = []
                lngs = []
                for i in range(1, 3):
                    a = m.groups()[0] + ' and ' + m.groups()[i] + ', Chicago, IL'
                    g = geocoder.google(a)
                    if g.latlng:
                        lats.append(g.lat)
                        lngs.append(g.lng)
            else:
                print 'No match'
        
        gmap.plot(lats, lngs, 'cornflowerblue', edge_width=10)  
    
    gmap.draw("mymap.html")          