from sqlalchemy import create_engine, select, and_
from create_db import projects, updates
import json
import geojson
import time
import branca
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
    cmap = branca.colormap.linear.Spectral.scale(0, n-1).to_step(n)
    cmap.caption = 'Job Status'
    m.add_child(cmap)
    
    feature_groups = []
    for t in types:
        feature_groups.append(folium.FeatureGroup(name=t))
    
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
        
        content = '<h2>%s</h2>' % (str(r1['id']))
        for loc in json.loads(r1['loc']):
            content += '<div>%s<div>' % (loc.strip())
        content += '<br>'
        
        date = ''
        ut = ''
        for r2 in res2:
            date = time.localtime(r2['date'])
            t = time.strftime('%Y-%m-%d', date)
            ut = r2['type']
            content += '<div>%s <font color="%s">%s</font></div>' % (t, cmap(types.index(ut)), ut)
        
        # get multiline string, add to map
        mls = geojson.loads(r1['geo'])
        c = folium.PolyLine(locations=mls.coordinates, color=cmap(types.index(ut)), weight=8, opacity=0.7)
        iframe = branca.element.IFrame(html=content, width=500, height=250)
        c.add_child(folium.Popup(iframe, max_width=500))
        #c.add_child(folium.Popup(str(r1['id'])))
        #m.add_child(c)
        c.add_to(feature_groups[types.index(ut)])
    
    for fg in feature_groups:
        fg.add_to(m)
    folium.LayerControl().add_to(m)
        
    # save map
    m.save('map.html')
