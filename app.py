from flask import Flask

import redis,json,csv,os
import pandas as pd
from datetime import datetime
from geopy import distance
from geopy.geocoders import ArcGIS

app=Flask(__name__)

url = "https://bit.ly/twmask"
orig = datetime(1970, 1, 1)
geolocator = ArcGIS(user_agent='twmask')

rhost = os.environment('RHOS')
rport = int(os.environment('RPORT'))
rpass = os.environment('RPASS')
redis = redis.Redis(host=rhost, port=rport, password=rpass)
"""
with open('ds.json') as f:
  ds = json.load(f)
ds_map = {}
for i in ds:
  ds_map[i['i']] = i['p']

def loadmaskdata():
  if redis.exists('mask:tw'):
      ret = redis.hgetall('mask:tw')
  else:
      md = pd.read_csv(url, encoding='utf-8')
      md_cols = ['id', 'name', 'address', 'tel', 'adult', 'child', 'lastsync']
      md.columns = md_cols
      md['now'] = int((datetime.now()-orig).total_seconds())
      md['pos'] = md.apply(lambda x: ds_map[x.id]]['p'] if (x.id in ds_map) else geolatlng(x.address), axis=1)
      md.to_csv('/tmp/md.csv', encoding='utf-8')
      ret = []
      with open('/tmp/md.csv') as f:
         rows = csv.reader(f)
         for r in rows:
           if r[0]:
             ret.append({ 'id': row[1], 'name': row[2], 'address': row[3],
                          'tel': row[4], 'adult': row[5], 'child': row[6],
                          'lastsync': row[7], 'now': row[8], 'pos': row[9]})
      redis.hmset('mask:tw', ret)
      redis.expire('mask:tw', 900)
  return ret

def calcDist(md, loc):
  for r in md:
    pos = r[9].replace('N','').replace(';W',';').split(';')
    dist = geodist(loc, (float(pos[0]),float(pos[1])))
    r['dist'] = dist

def geolatlng(addr):
  if redis.exists(f'a:{addr}'):
    location = redis.hgetall(f'a:{addr}')
  else:
    location = geolocator.geocode(addr)
    redis.hmset(f'a:{addr}',location)
  return "N{};W{}".format(location.latitude,location.longitude)

def geodist(a, b):
  return distance.distance(a, b).km

@app.route("/twmask")
def twmask():
  md = loadmaskdata()
  loc = (25.026536999999998, 121.544442)
  calcDist(md, loc)
  ret = sorted(md[1:], key=lambda r: r['dist'])[:5]
  return json.dumps(ret)

"""

@app.route("/")
def home():
  return "Hello Flask 2"

@app.route("/test")
def test():
  return "This is Test"

if __name__=="__main__":
  app.run()