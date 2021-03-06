from sqlalchemy import create_engine, select, and_
from create_db import projects, updates
import geojson
import json
#import gmplot
import time
from pylab import cm, matplotlib


if __name__ == '__main__':
    # initialize db engine
    db = create_engine('sqlite:///water_alert.db', echo=False)
    
    #gmap = gmplot.GoogleMapPlotter(41.8781, -87.6298, 12)
    
    types = [u'Construction Mobilization', \
        u'Pipe Installation Completed', \
        u'Concrete Cap Complete', \
        u'Street Restoration', \
        u'Partner Agency Street Restoration', \
        u'Water Service Transfer Complete', \
        u'Pressure and Disinfection Tests Approved', \
        u'Water Main Project Completed']
    
    years = range(2011, 2018)
    cmap = cm.get_cmap('plasma', len(types))
    colors = [matplotlib.colors.rgb2hex(cmap(i)[:3]) for i in range(cmap.N)]
    cdict = dict(zip(types, colors))
    
    # check for job id in projects table
    conn = db.connect()
    s = select([projects])
    res1 = conn.execute(s).fetchall()
    conn.close()
    
    map_name = 'map.html'
    f = open(map_name, 'w')
    f.write("""<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Chicago Lead Map</title>
    <style>
      /* Always set the map height explicitly to define the size of the div
       * element that contains the map. */
      #map {
        height: 100%;
      }
      /* Optional: Makes the sample page fill the window. */
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
      #legend {
        font-family: Arial, sans-serif;
        font-size: 15px;
        font-weight: bold;
        background: #fff;
        padding: 10px;
        margin: 10px;
        border: 3px solid #000;
      }
      #legend h3 {
        margin-top: 0;
      }
      #legend img {
        vertical-align: middle;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <div id="legend"><h3>Legend</h3></div>
    <script>
      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 12,
          center: {lat: 41.8781, lng: -87.6298},
          mapTypeId: 'terrain'
        });

        var infowindow = new google.maps.InfoWindow();
        var marker, content, mainCoordinates, mainPath;  
        var legend = document.getElementById('legend');
        """)
    f.close()
    
    for r1 in res1:
        if not r1['geo']:
            continue
        
        mls = geojson.loads(r1['geo'])
            
        content = '<h3>' + str(r1['id']) + '</h3>'
        for loc in json.loads(r1['loc']):
            content += '<div>' + loc.strip() + '<div>'
        content += '<br>'
        
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
            content += """<div>%s <font color="%s">%s</t></div>""" % (t, cdict[ut], ut)
            #content += '<div>' + t + '</div>'
          
        f = open(map_name, 'a')
        f.write(""" 
        
        marker = new google.maps.Marker({
          position: {lat: %f, lng: %f},
          map: map,
          visible: false,
          icon: 'https://maps.google.com/mapfiles/ms/micons/drinking_water.png'
        });
        
        var content = '%s';
        
        google.maps.event.addListener(marker, 'click', (function(marker, content, infowindow) { 
          return function() {
              infowindow.setContent(content);
              infowindow.open(map, marker);
          };
        })(marker, content, infowindow));  
        """ % (mls.coordinates[0][0][0], mls.coordinates[0][0][1], content))
        f.close()
        
        for l in mls.coordinates:
            [lat, lng] = map(list, zip(*l))
            
            f = open(map_name, 'a')
            f.write("""     
        
        mainCoordinates = [
          {lat: %f, lng: %f},
          {lat: %f, lng: %f}
        ];
            
        mainPath = new google.maps.Polyline({
          path: mainCoordinates,
          geodesic: true,
          strokeColor: '%s',
          strokeOpacity: 0.67,
          strokeWeight: 10
        });
            
        mainPath.setMap(map);
        
        google.maps.event.addListener(mainPath, 'click', (function(marker, content, infowindow) { 
          return function() {
              infowindow.setContent(content);
              infowindow.open(map, marker);
          };
        })(marker, content, infowindow));  
        """ % (lat[0], lng[0], lat[1], lng[1], cdict[ut]))
            f.close()
    
            # plot segment
            #gmap.plot(lat, lng, 'lime', edge_width=5)
    
    for t in types:
        f = open(map_name, 'a')
        f.write("""    
        var div = document.createElement('div');
        div.innerHTML = '<font color="%s">%s</font>';
        legend.appendChild(div);""" % (cdict[t], t))
        f.close()

    f = open(map_name, 'a')
    f.write("""  
        map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);
      }
    </script>
    <script async defer
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDDVhHFe52p2Ch3s9aVQ8HNGmFSpsU9GrQ&callback=initMap">
    </script>
  </body>
</html>
""")
    f.close()
    
    #gmap.draw('wa-map.html')          