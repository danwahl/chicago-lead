import httplib2
from apiclient import discovery, errors
import quickstart
import base64
import bs4
import requests
import time
import re
import geocoder
import geojson
import json
from sqlalchemy import create_engine, select, and_
from create_db import projects, updates

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
    
    # initialize db engine
    db = create_engine('sqlite:///water_alert.db', echo=False)
    
    #gmap = gmplot.GoogleMapPlotter(41.8781, -87.6298, 12)
    
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
        
        # wait a bit before the next one
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
        project_id = int(soup.find_all('span')[0].contents[0])
        
        # check for job id in projects table
        conn = db.connect()
        s = select([projects], and_(projects.c.id == project_id))
        res = conn.execute(s).fetchall()
        conn.close()
        
        # if not in database, geocode and add
        if not res:
            loc = []
            num = 0
            mls = geojson.MultiLineString()
            # find cross streets
            segments = soup.find_all('li')
            for s in segments:
                success = True
                m = p.match(s.contents[0])  
                if m:
                    #print 'Match found: ', m.groups()
                    ls = geojson.LineString()
                    for i in range(1, 3):
                        a = m.groups()[0] + ' & ' + m.groups()[i] + ', Chicago, IL'
                        g = geocoder.google(a)
                        if g.json['status'] == 'OK':
                            if g.json['quality'] == 'intersection':
                                ls.coordinates.append(g.latlng)
                            else: success = False
                        else: success = False
                    
                    # update geo info
                    num += 1
                    loc.append(re.sub(' +', ' ', s.contents[0]).encode('ascii', 'ignore'))
                    if success:
                        mls.coordinates.append(ls.coordinates)
                    else:
                        print str(project_id) + ' ' + s.contents[0]
                        mls.coordinates.append([])
            
            # insert into table   
            conn = db.connect()
            ins = projects.insert(values=dict(id=project_id, num=num, loc=json.dumps(loc), geo=geojson.dumps(mls)))
            conn.execute(ins)
            conn.close()  
        
        
        # add project update and archive
        update = soup.find_all('h2')[0].contents[0].encode('ascii', 'ignore')
        date = int(float(msg['internalDate'])/10e3)
        
        # insert into table   
        conn = db.connect()
        ins = updates.insert(values=dict(id=project_id, date=date, update=update))
        conn.execute(ins)
        conn.close()  
        
        ModifyMessage(service, 'me', message['id'], msg_labels)
                    
        # plot segment
        #gmap.plot(lats, lngs, 'cyan', edge_width=10)  
    
    #gmap.draw('mymap.html')          