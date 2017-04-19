from sqlalchemy import create_engine, select, and_
from create_db import projects, updates
import geojson
import json
#import gmplot
import time


if __name__ == '__main__':
    # initialize db engine
    db = create_engine('sqlite:///water_alert.db', echo=False)
    
    #gmap = gmplot.GoogleMapPlotter(41.8781, -87.6298, 12)
    
    # check for job id in projects table
    conn = db.connect()
    s = select([projects])
    res = conn.execute(s).fetchall()
    conn.close()
    
    f = open('map.html', 'w')
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
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script>
      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 12,
          center: {lat: 41.878100, lng: -87.629800},
          mapTypeId: 'terrain'
        });

        var infowindow = new google.maps.InfoWindow();
        var marker, content, mainCoordinates, mainPath;        
        """)
    f.close()
    
    for r in res:
        mls = geojson.loads(r['geo'])
            
        content = '<h3>' + str(r['id']) + '</h3>'
        for loc in json.loads(r['loc']):
            content += '<div>' + loc.strip() + '<div>'
        content += '<br>'
        
        # check for job id in projects table
        conn = db.connect()
        s = select([updates], and_(updates.c.id == r['id']))
        res = conn.execute(s).fetchall()
        conn.close()
        
        for r in res:
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r['date']))
            content += '<div>' + t + ' - ' + r['update'] + '<div>'
          
        f = open('map.html', 'a')
        f.write(""" 
        
        marker = new google.maps.Marker({
          position: {lat: %f, lng: %f},
          map: map
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
            
            f = open('map.html', 'a')
            f.write("""     
        
        mainCoordinates = [
          {lat: %f, lng: %f},
          {lat: %f, lng: %f}
        ];
            
        mainPath = new google.maps.Polyline({
          path: mainCoordinates,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 0.5,
          strokeWeight: 4
        });
            
        mainPath.setMap(map);""" % (lat[0], lng[0], lat[1], lng[1]))
            f.close()
    
            # plot segment
            #gmap.plot(lat, lng, 'lime', edge_width=5)

    f = open('map.html', 'a')
    f.write("""    
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