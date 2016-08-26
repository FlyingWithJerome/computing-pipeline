'''
Created on Aug 5, 2016

@author: Zongyang Li
'''
import sys
import os
import zipfile
from os import system, path



# Define that GPS bounds of interest -- we'll ignore any data that are outside of these bounds
# Order is: (SW_lat,SW_lng,NE_lat,NE_lng)
# full field
# GPS_BOUNDS = (33.072616729424254, -111.97499111294746, 33.07404171941707, -111.9747644662857)

# designate the folder name for saving the tiles
TILE_FOLDER_NAME = 'tiles_left'


def createVrt(base_dir,tif_file_list):
    # Create virtual tif for the files in this folder
    # Build a virtual TIF that combines all of the tifs in tif_file_list
    print "\tCreating virtual TIF..."
    try:
        vrtPath = path.join(base_dir,'virtualTif.vrt')
        cmd = 'gdalbuildvrt -srcnodata "-99 -99 -99" -overwrite -input_file_list ' + tif_file_list +' ' + vrtPath
        system(cmd)
    except Exception as ex:
        fail("\tFailed to create virtual tif: " + str(ex))

def createMapTiles(base_dir,NUM_THREADS):
    # Create map tiles from the virtual tif
    # For now, just creating w/ local coordinate system. In the future, can make these actually georeferenced.
    print "\tCreating map tiles..."
    try:
        vrtPath = path.join(base_dir,'virtualTif.vrt')
        cmd = 'python gdal2tiles_parallel.py --processes=' + str(NUM_THREADS) + ' -l -n -e -f JPEG -z "18-28" -s EPSG:4326 ' + vrtPath + ' ' + path.join(base_dir,TILE_FOLDER_NAME)
        system(cmd)
    except Exception as ex:
        fail("Failed to generate map tiles: " + str(ex))


def file_len(fname):
    with open(fname) as f:
        for i in enumerate(f):
            pass
    return i+1

def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')    
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)     
            zipf.write(pathfile, arcname)
    zipf.close()

        
def fail(reason):
    print >> sys.stderr, reason
    

def generate_googlemaps(base_dir):
        args = path.join(base_dir, TILE_FOLDER_NAME)

        s = """
            <!DOCTYPE html>
                <html>
                  <head>
                    <title>Map Create By Left Sensor</title>
                    <meta name="viewport" content="initial-scale=1.0">
                    <meta charset="utf-8">
                    <style>
                      html, body {
                        height: 100%%;
                        margin: 0;
                        padding: 0;
                      }
                      #map {
                        height: 100%%;
                      }
                    </style>
                  </head>
                  <body>
                    <div id="map"></div>
                    <script>
                      function initMap() {
                          var MyCenter = new google.maps.LatLng(33.0726220351,-111.974918861);
                  var map = new google.maps.Map(document.getElementById('map'), {
                    center: MyCenter,
                    zoom: 18,
                    streetViewControl: false,
                    mapTypeControlOptions: {
                      mapTypeIds: ['Terra']
                    }
                  });
                  
                
                
                  var terraMapType = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        var bound = Math.pow(2, zoom);
                        var y = bound-coord.y-1;
                       return '%s' +'/' + zoom + '/' + coord.x + '/' + y + '.jpg';
                    },
                    tileSize: new google.maps.Size(256, 256),
                    maxZoom: 28,
                    minZoom: 18,
                    radius: 1738000,
                    name: 'Terra'
                  });
                  
                  map.mapTypes.set('Terra', terraMapType);
                  map.setMapTypeId('Terra');
                }
                
                    </script>
                    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDJW9xwkAN3sfZE4FvGGLcgufJO9oInIHk&callback=initMap"async defer></script>
                  </body>
                </html>
            """ % args
        
        f = open(path.join(base_dir, 'opengooglemaps.html'), 'w')
        f.write(s)
        f.close()

        return s

