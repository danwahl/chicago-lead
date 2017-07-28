from sqlalchemy import create_engine, select, and_
from create_db import projects, updates
import json
import geojson
import time
import branca.colormap as cm
import folium


if __name__ == '__main__':
    # initialize db engine
    db = create_engine('sqlite:///water_alert.db', echo=False)
    
    # create map
    lat = 41.8781
    lon = -87.6298
    zoom_start = 12
    m = folium.Map(location=[lat, lon], tiles="Cartodb Positron", zoom_start=zoom_start)
    
    # type color map
    types = [u'Construction Mobilization', \
        u'Pipe Installation Completed', \
        u'Concrete Cap Complete', \
        u'Street Restoration', \
        u'Partner Agency Street Restoration', \
        u'Water Service Transfer Complete', \
        u'Pressure and Disinfection Tests Approved', \
        u'Water Main Project Completed']
    n = len(types)
    cmap = cm.linear.Spectral.scale(0, n-1).to_step(n)
    cmap.caption = 'Job Status'
    m.add_child(cmap)
    
    # check for job id in projects table
    conn = db.connect()
    s = select([projects])
    res1 = conn.execute(s).fetchall()
    conn.close()
    
    # iterate through jobs
    for r1 in res1:
        # check for geographic info
        if not r1['geo']:
            continue
            
        # check for job id in projects table
        conn = db.connect()
        s = select([updates], and_(updates.c.id == r1['id']))
        res2 = conn.execute(s).fetchall()
        conn.close()
        
        date = ''
        ut = ''
        for r2 in res2:
            date = time.localtime(r2['date'])
            t = time.strftime('%Y-%m-%d', date)
            ut = r2['type']
        
        # get multiline string, add to map
        mls = geojson.loads(r1['geo'])
        c = folium.PolyLine(locations=mls.coordinates, color=cmap(types.index(ut)), weight=8, opacity=0.7)
        c.add_child(folium.Popup(str(r1['id'])))
        m.add_child(c)

    # save map
    m.save('map.html')
