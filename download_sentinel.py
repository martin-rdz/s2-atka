#! /usr/bin/python


import argparse
import requests
import shutil
import pprint
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path
import datetime
import toml

#curl --location --request POST 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' 
# --header 'Content-Type: application/x-www-form-urlencoded' 
# --data-urlencode 'grant_type=password' 
# --data-urlencode 'username=' 
# --data-urlencode 'password=' 
# --data-urlencode 'client_id=cdse-public'


def get_token(config):
    headers = {
    "Content-Type":"application/x-www-form-urlencoded",
    }
    data = {
    "grant_type":"password",
    "username":config['username'],
    "password":config['password'],
    "client_id":"cdse-public",
    }
    
    
    url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
    
    response = requests.post(url, data=data, headers=headers, verify=True)
    tokens = response.json()
    print(response.json())
    pprint.pprint(tokens)
    return tokens


def get_features(dt_start, dt_end, lat, lon, radius=5000):

    # cataloque description
    # https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/describe.xml
    #https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?processingLevel=S2MSI1C&cloudCover=[0,100]&startDate=2023-02-21&completionDate=2023-02-27&maxRecords=10&lat=-70.6&lon=-8.0&radius=5000
    base_url = 'https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json'
    query = f'?processingLevel=S2MSI1C&cloudCover=[0,100]&startDate={dt_start:%Y-%m-%d}&completionDate={dt_end:%Y-%m-%d}&maxRecords=50&lat={lat}&lon={lon}&radius={radius}'
    
    print('query url: ', base_url + query)
    response = requests.get(base_url + query)
    
    found_collections = response.json()
    print('no collections ', len(found_collections['features']))
    
    for f in found_collections['features']:
        print('id', f['id'])
        print('  startDate', f['properties']['startDate'])
        print('  title', f['properties']['title'])
    
    return found_collections['features']
    


def download_features(feature, outpath):


    print('download', feature['properties']['title'])
    dt = datetime.datetime.strptime(feature['properties']['startDate'][:-1], "%Y-%m-%dT%H:%M:%S.%f")

    op = outpath / f"{dt:%Y%m%d}"
    print(op)

    headers = { 'user-agent' : "" }
    headers['Authorization'] = 'Bearer ' + tokens['access_token']
    # {'Date': 'Tue, 28 Feb 2023 18:01:39 GMT', 'Content-Type': 'application/zip', 'Content-Length': '658457947', 'Connection': 'keep-alive', 'Content-Disposition': 'attachment; filename=S2B_MSIL1C_20230223T093009_N0509_R107_T29DNB_20230223T141120.zip', 'Accept-Ranges': 'bytes', 'Strict-Transport-Security': 'max-age=15724800; includeSubDomains', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, PATCH, OPTIONS', 'Access-Control-Allow-Headers': 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization', 'Access-Control-Max-Age': '1728000'}
    url = f"http://catalogue.dataspace.copernicus.eu/odata/v1/Products({feature['id']})/$value"
    print('url', url)

    session = requests.Session()
    session.headers.update({'Authorization': f"Bearer {tokens['access_token']}"})

    response = session.get(url, allow_redirects=False)
    while response.status_code in (301, 302, 303, 307):
        url = response.headers['Location']
        response = session.get(url, allow_redirects=False)

    f = session.get(url, verify=False, allow_redirects=True)

    #response = requests.get(url, stream=True, headers=headers)
    print('response headers ', response.headers)
    #if response.headers['Content-Type'] == 'application/zip':
    #with open('test.zip', 'wb') as out_file:
        #shutil.copyfileobj(response.raw, out_file)
    #    with ZipFile(BytesIO(f.content)) as zfile:
    #        zfile.extractall(op)
    with ZipFile(BytesIO(f.content)) as zfile:
        zfile.extractall(op)
    #else:
    #    print(response.content)
    #    print('wait for input')
    #    input()
    


parser = argparse.ArgumentParser(
                    prog = 'plot_overpass',
                    description = '',
                    epilog = '')

parser.add_argument('date', help='date to download %Y%m%d')
parser.add_argument('-r', '--radius', type=int, default=5000, help='Radius around the POI in m')

args = parser.parse_args()

print(args.date)

#dt_start = datetime.datetime(2022, 9, 1)
#dt_end = datetime.datetime(2022, 12, 1)
#dt_start = datetime.datetime(2023, 4, 5)
#dt_end = datetime.datetime(2023, 4, 9)
#dt_start = datetime.datetime(2023, 8, 30)
#dt_end = datetime.datetime(2023, 9, 2)
dt_start = datetime.datetime.strptime(args.date, "%Y%m%d")
dt_end = dt_start + datetime.timedelta(hours=24)
lat = -70.6
lon = -8.0
radius = args.radius 
features = get_features(dt_start, dt_end, lat, lon, radius)

outpath = Path('data_sentinel2')

config =  toml.load('config.toml')

for f in features:
    # token is valid only very short time -> update frequently
    tokens = get_token(config)
    download_features(f, outpath)



