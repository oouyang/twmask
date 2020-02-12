from flask import Flask, request, render_template

import redis,json,csv,os,geocoder
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
      redis.expire('mask:tw', 900)
  return ret

def calcDist(md, loc):
  for r in md:
    pos = r['pos'].replace('N','').replace(';W',';').split(';')
    dist = geodist(loc, (float(pos[0]),float(pos[1])))
    r['dist'] = dist

def geolatlng(addr):
  if redis.exists(f'a:{addr}'):
    location = json.loads(redis.get(f'a:{addr}'))
  else:
    #location = geolocator.geocode(addr)
    location = geocoder.arcgis(addr).json
    redis.set(f'a:{addr}',json.dumps(location))
  return "N{};W{}".format(location['lat'],location['lng'])

def geodist(a, b):
  return distance.distance(a, b).km

@app.route("/twmask")
def twmask():
  lat = request.args.get('lat')
  lng = request.args.get('lng')
  if lat and lng:
      #return "({lat},{lng})"
      md = loadmaskdata()
      loc = (25.026536999999998, 121.544442)
      loc = (lat, lng)
      calcDist(md, loc)
      ret = sorted(md[1:], key=lambda r: r['dist'])[:5]
      return json.dumps(ret)
  else:
      return render_template('twmask.html')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/test")
def test():
  addr=request.args.get('addr')
  return geolatlng(addr)

if __name__=="__main__":
  app.run()