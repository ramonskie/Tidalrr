#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   lidarr.py
@Time    :   2023/04/12
@Author  :   lejacobroy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import sys
import getopt
import aigpy

from events import *
from settings import *
#from model import *


def getMissingAlbums(URL: str, API: str):
    # http://pomelo:8686/api/v1/wanted/missing?apikey=LIDARR_APIKEY

    #print(urlpre + path, header, params)
    #print(URL+'/api/v1/wanted/missing?apikey='+API)
    respond = requests.get(URL+'/api/v1/wanted/missing?apikey='+API)
    #print(respond)
    
    result = json.loads(respond.text)

    albums = [Album()]

    if 'status' not in result:
        #print(result)
        
        for record in result["records"]:
            art = Artist()
            art.name = record['artist']['artistName']

            alb = Album()
            alb.title = record['title']
            alb.duration = record['duration']/60
            alb.numberOfTracks = record['releases'][0]['trackCount']
            alb.path = record['artist']['path']
            alb.artist = art

            albums.append(alb)
        #print(aigpy.model.modelListToDictList(albums))
    #print(aigpy.model.modelListToDictList(albums))
    return albums

    # returns this:
    # extract usefull info:
    #   - Artist, Title, Path
    # match "Artist - Album Title" with a Tidal ID (API Search?)
    # https://github.com/Fokka-Engineering/TIDAL/wiki/search-artists -> get artist ID
    #    -> https://api.tidalhifi.com/v1/search/artists?query='Coldplay'&limit=1&countryCode=CA
    # https://github.com/Fokka-Engineering/TIDAL/wiki/search-albums -> get album ID and filter by artist ID
