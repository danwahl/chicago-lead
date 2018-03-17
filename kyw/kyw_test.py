import pandas as pd
import numpy as np
import geocoder
import requests
import time

NUM_RETRIES = 5

if __name__ == '__main__':
    # set api key as environment variable
    key = 'AIzaSyAdbz4HJtr4zOUSsDecW9aqyi3RERTbk20'
    
    # read both sheets from cip file and combine
    cip = pd.read_excel('2017 Water CIP.xlsx', sheetname=['In House', 'Term Agreement'], skiprows=4, index_col=0, \
        names=['on', 'from', 'to', 'start', 'actual_start', 'end', 'actual_end', 'length'])
    cip['In House']['in_house'] = True
    cip['Term Agreement']['in_house'] = False
    cip = pd.concat(cip.values())
    cip.index.name = 'bes'
    cip['actual_start'] = cip['actual_start'].notnull()
    cip['actual_end'] = cip['actual_end'].notnull()
    
    # drop any nan in address section
    cip.dropna(axis=0, how='any', subset=['on', 'to', 'from'], inplace=True)
    
    # iterate through cip, geocode
    cip['from_lat'] = np.nan
    cip['from_lng'] = np.nan
    cip['to_lat'] = np.nan
    cip['to_lng'] = np.nan
    for i in range(len(cip)): 
        # find gps coordinates, add to linestring
        for j in ['from', 'to']:
            latlng = [np.nan, np.nan]
            
            # get intersection
            a = cip.iloc[i]['on'] + ' & ' + cip.iloc[i][j] + ', Chicago, IL'
            
            # call geocoder
            for _ in range(NUM_RETRIES):
                try:
                    g = geocoder.google(a, key=key)
                    break
                except requests.exceptions.Timeout:
                    time.sleep(1)
            
            success = True
            if g.json['status'] == 'OK':
                latlng = g.latlng
            else:
                print a
                print 'geocoding not successful'
                print g.json['status']
        
            # add to row
            cip.iloc[i, cip.columns.get_loc(j + '_lat')] = latlng[0]
            cip.iloc[i, cip.columns.get_loc(j + '_lng')] = latlng[1]
    
    # write to csv
    cip.to_csv('cip.csv')
    
    # read water quality data
    wq = pd.read_excel('WQ_Study_Results.xlsx', sheetname='Initial', skiprows=2, index_col=0, \
        names=['address', '1st', '4th', '6th', '5min', '5min2'], skip_footer=3)    
    wq.index.name = 'date'
    
    # make measurements numeric
    for i in ['1st', '4th', '6th', '5min', '5min2']:
        wq[i] = wq[i].replace('<0.3', '0.0')
        wq[i] = pd.to_numeric(wq[i], errors='coerce')
    wq.dropna(axis=0, subset=['1st', '4th', '6th', '5min', '5min2'], how='all', inplace=True)
    
    # add study column, remove double asterix
    wq['study'] = ~wq['address'].str.contains('\*\*')
    wq['address'].replace(regex=True, inplace=True, to_replace='\*\*', value='')
    
    # add partial column, remove unicode circumflex
    wq['partial'] = wq['address'].str.contains(u'ˆ')
    wq['address'].replace(regex=True, inplace=True, to_replace=u'ˆ', value='')
    
    # convert XX to 50 (place address mid-block)
    wq['address'].replace(regex=True, inplace=True, to_replace=r'XX', value=r'50')
    
    # split out site
    wq[['address', 'site']] = wq['address'].str.split('Site', expand=True)
    
    # iterate through wq, geocode
    wq['lat'] = np.nan
    wq['lng'] = np.nan
    for i in range(len(wq)):
        laglng = [np.nan, np.nan]
        
        # get address
        a = wq.iloc[i]['address'] + ', Chicago, IL'
        
        # call geocoder
        for _ in range(NUM_RETRIES):
            try:
                g = geocoder.google(a, key=key)
                break
            except requests.exceptions.Timeout:
                time.sleep(1)
        
        if g.json['status'] == 'OK':
            latlng = g.latlng
        else:
            print a
            print 'geocoding not successful'
            print g.json['status']
        
        # add to row
        wq.iloc[i, wq.columns.get_loc('lat')] = latlng[0]
        wq.iloc[i, wq.columns.get_loc('lng')] = latlng[1]
    
    # write to csv
    wq.to_csv('wq.csv')
                