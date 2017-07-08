# -*- coding: utf-8 -*-
"""
Created on Fri Jul 07 17:02:16 2017

@author: dan
"""

import pandas as pd
import re

import geocoder
import geojson
import json

from sqlalchemy import create_engine
from create_db import projects, updates

if __name__ == '__main__':
    p = re.compile('(.*)\sfrom\s(.*)\sto\s(.*)')
            
    df = pd.read_csv('25th_ward.csv', delimiter='|', parse_dates=[0])
    
        # initialize db engine
    db = create_engine('sqlite:///25th_ward.db', echo=False)
    
    for index, row in df.iterrows():
        street = row['street'].split(':')
        
        loc = []
        num = 0
        mls = geojson.MultiLineString()
        
        for s in street:
            m = p.match(s)
            success = True
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
                loc.append(re.sub(' +', ' ', s).encode('ascii', 'ignore'))
                if success:
                    mls.coordinates.append(ls.coordinates)
                else:
                    print str(row['date']) + ' ' + a
                    mls.coordinates.append([])
                
        '''
        # insert into table   
        conn = db.connect()
        ins = projects.insert(values=dict(id=int(index), num=num, loc=json.dumps(loc), geo=geojson.dumps(mls)))
        conn.execute(ins)
        conn.close()
        '''
        
        # add project update and archive
        update = ''
        date = int(row['date'].value//10**9)
        
        # insert into table   
        conn = db.connect()
        ins = updates.insert(values=dict(id=int(index), date=date, update=update))
        conn.execute(ins)
        conn.close()  
        