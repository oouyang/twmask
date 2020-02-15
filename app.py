from flask import Flask, request, render_template

import redis,json,csv,os,geocoder,psycopg2
import pandas as pd
from datetime import datetime
from geopy import distance
from geopy.geocoders import ArcGIS

app=Flask(__name__)

url = "https://bit.ly/twmask"
orig = datetime(1970, 1, 1)
#geolocator = ArcGIS(user_agent='twmask')
rhost = os.environ['RHOST']
rport = int(os.environ['RPORT'])
rpass = os.environ['RPASS']
redis = redis.Redis(host=rhost, port=rport, password=rpass)

db_url = os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url, sslmode='require')

with open('ds.json') as f:
  ds = json.load(f)


ds_map = {}


for i in ds:
  ds_map[i['i']] = i['p']


def loadmaskdata():
  if redis.exists('mask:tw'):
      ret = json.loads(redis.get('mask:tw'))
  else:
      md = pd.read_csv(url, encoding='utf-8')
      md_cols = ['id', 'name', 'address', 'tel', 'adult', 'child', 'lastsync']
      md.columns = md_cols
      md['now'] = int((datetime.now()-orig).total_seconds())
      md['pos'] = md.apply(lambda x: ds_map[x.id] if (x.id in ds_map) else geolatlng(x.address), axis=1)
      md.to_csv('/tmp/md.csv', encoding='utf-8')
      ret = []
      with open('/tmp/md.csv') as f:
         rows = csv.reader(f)
         for r in rows:
           if r[0]:
             ret.append({ 'id': r[1], 'name': r[2], 'address': r[3],
                          'tel': r[4], 'adult': r[5], 'child': r[6],
                          'lastsync': r[7], 'now': r[8], 'pos': r[9]})
      redis.set('mask:tw', json.dumps(ret))
      redis.expire('mask:tw', 3600)
  return ret

def calcDist(md, loc):
  for r in md:
    pos = r['pos'].replace('N','').replace(';E',';').split(';')
    dist = geodist(loc, (float(pos[0]),float(pos[1])))
    r['dist'] = dist

def geolatlng(addr):
  if redis.exists(f'a:{addr}'):
    location = json.loads(redis.get(f'a:{addr}'))
  else:
    #location = geolocator.geocode(addr)
    location = geocoder.arcgis(addr).json
    redis.set(f'a:{addr}',json.dumps(location))
  return "N{};E{}".format(location['lat'],location['lng'])

def geodist(a, b):
  return distance.distance(a, b).km

def logsql(ip, lat, lng):
  cursor = conn.cursor()
  insert_query = """insert into log (ip,lat,lng) values (%s,%s,%s)"""
  record_to_insert = (ip,lat,lng)
  cursor.execute(insert_query, record_to_insert)
  conn.commit()

@app.route("/twmask")
def twmask():
  lat = request.args.get('lat')
  lng = request.args.get('lng')
  hits = request.args.get('hits', default=5, type=int)
  if lat and lng:
      #return "({lat},{lng})"
      md = loadmaskdata()
      loc = (25.026536999999998, 121.544442)
      loc = (lat, lng)
      calcDist(md, loc)
      ret = sorted(md[1:], key=lambda r: r['dist'])[:hits]
      ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
      logsql(ip, lat,lng)
      return json.dumps(ret)
  else:
      return render_template('twmask.html')

@app.route("/")
def home():
    return render_template('twmask.html')

@app.route("/map")
def map():
    return render_template('map.html')

@app.route("/latlng")
def latlng():
  addr=request.args.get('addr','新北市景平路188號')
  return geolatlng(addr)

if __name__=="__main__":
  app.run()


  """
  Geographical Searches
  https://docs.vespa.ai/documentation/geo-search.html
  https://docs.vespa.ai/documentation/reference/search-definitions-reference.html#type:position
  https://docs.vespa.ai/documentation/reference/search-api-reference.html#geographical-searches
  https://docs.vespa.ai/documentation/reference/document-json-format.html
  https://docs.vespa.ai/documentation/reference/rank-features.html#distanceToPath(name).distance
Restrict
  a position + radius or a bounding box

Rank
  distance(latlong)


create (create if nonexistent)
Updates to nonexistent documents are supported using create. Refer to writing to Vespa for semantics.

{
    "update": "id:mynamespace:music::http://music.yahoo.com/bobdylan/BestOf",
    "create": true,
    "fields": {
        "title": {
            "assign": "The best of Bob Dylan"
        }
    }
}
  """