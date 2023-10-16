#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  events.py
@Date    :  2022/06/10
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""

import aigpy
import time

from model import *
from enums import *
from tidal import *
from printf import *
from download import *
from paths import *

'''
=================================
START DOWNLOAD
=================================
'''


def start_album(obj: Album):
    Printf.album(obj)
    tracks = TIDAL_API.getItems(obj.id, Type.Album)
    if SETTINGS.saveAlbumInfo:
        downloadAlbumInfo(obj, tracks)
    if SETTINGS.saveCovers and obj.cover is not None:
        downloadCover(obj)
    downloadTracks(tracks, obj)
"""     if SETTINGS.downloadVideos:
        downloadVideos(videos, obj) """

def start_album_search(obj: Album):
    print(obj.title)
    #print(aigpy.model.modelToDict(obj))
    album = TIDAL_API.searchAlbum(obj)
    if album is not None:
        start_album(album)
    #print(aigpy.model.modelToDict(album))

def start_playlist_sync(UserId=None):
    playlists = TIDAL_API.getPlaylistsAndFavorites(UserId)
    for playlist in playlists:
        if playlist.title is not None:
            start_playlist(playlist)

def start_track(obj: Track):
    album = TIDAL_API.getAlbum(obj.album.id)
    if SETTINGS.saveCovers:
        downloadCover(album)
    downloadTrack(obj, album)


""" def start_video(obj: Video):
    downloadVideo(obj, obj.album) """


def start_artist(obj: Artist):
    albums = TIDAL_API.getArtistAlbums(obj.id, SETTINGS.includeEP)
    Printf.artist(obj, len(albums))
    for item in albums:
        start_album(item)


def start_playlist(obj: Playlist):
    Printf.playlist(obj)
    # here we have the playlist object, we can export it to json
    #print(aigpy.model.modelToDict(obj))
    # save this to playlist.json
    data = aigpy.model.modelToDict(obj)

    path = getPlaylistPath(obj)

    aigpy.file.write(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.json', json.dumps(data), 'w+')

    Printf.info('Saved playlist json info to : '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.json')

    tracks = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    paths = downloadTracks(tracks, None, obj)

    with open(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u', 'w') as f:
        #f.write('#EXTM3U\n')
        for i,item in enumerate(paths, start=1):
            f.write(str(getTrueHomePath())+'/'+item+'\n')
    Printf.success('Done generating m3u playlist file: '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u')

    # Generate the playlist file
    with open(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u8', 'w') as f:
        f.write('#EXTM3U\n')
        for i,item in enumerate(aigpy.model.modelListToDictList(tracks), start=1):
            track = aigpy.model.dictToModel(item, Track())
            track.trackNumberOnPlaylist = i
            filename = path[i-1]
            f.write(f'#EXTINF:{item["duration"]},{item["artist"]["name"]} - {item["title"]}\n')
            f.write(str(getTrueHomePath())+'/'+filename+'\n') 
    Printf.success('Done generating m3u8 playlist file: '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u8')

def start_mix(obj: Mix):
    Printf.mix(obj)
    downloadTracks(obj.tracks, None, None)
"""     downloadVideos(obj.videos, None, None) """


def start_file(string):
    txt = aigpy.file.getContent(string)
    if aigpy.string.isNull(txt):
        Printf.err("Nothing can read!")
        return
    array = txt.split('\n')
    for item in array:
        if aigpy.string.isNull(item):
            continue
        if item[0] == '#':
            continue
        if item[0] == '[':
            continue
        start(item)


def start_type(etype: Type, obj):
    if etype == Type.Album:
        start_album(obj)
    elif etype == Type.Track:
        start_track(obj)
    elif etype == Type.Artist:
        start_artist(obj)
    elif etype == Type.Playlist:
        start_playlist(obj)
    elif etype == Type.Mix:
        start_mix(obj)


def start(string):
    if aigpy.string.isNull(string):
        Printf.err('Please enter something.')
        return

    strings = string.split(" ")
    for item in strings:
        if aigpy.string.isNull(item):
            continue
        if os.path.exists(item):
            start_file(item)
            return

        try:
            etype, obj = TIDAL_API.getByString(item)
        except Exception as e:
            Printf.err(str(e) + " [" + item + "]")
            return

        try:
            start_type(etype, obj)
        except Exception as e:
            Printf.err(str(e))


'''
=================================
CHANGE SETTINGS
=================================
'''


def changePathSettings():
    Printf.settings()
    SETTINGS.downloadPath = Printf.enterPath(
        LANG.select.CHANGE_DOWNLOAD_PATH,
        LANG.select.MSG_PATH_ERR,
        '0',
        SETTINGS.downloadPath)
    SETTINGS.albumFolderFormat = Printf.enterFormat(
        LANG.select.CHANGE_ALBUM_FOLDER_FORMAT,
        SETTINGS.albumFolderFormat,
        SETTINGS.getDefaultPathFormat(Type.Album))
    SETTINGS.playlistFolderFormat = Printf.enterFormat(
        LANG.select.CHANGE_PLAYLIST_FOLDER_FORMAT,
        SETTINGS.playlistFolderFormat,
        SETTINGS.getDefaultPathFormat(Type.Playlist))
    SETTINGS.trackFileFormat = Printf.enterFormat(
        LANG.select.CHANGE_TRACK_FILE_FORMAT,
        SETTINGS.trackFileFormat,
        SETTINGS.getDefaultPathFormat(Type.Track))
    """ SETTINGS.videoFileFormat = Printf.enterFormat(
        LANG.select.CHANGE_VIDEO_FILE_FORMAT,
        SETTINGS.videoFileFormat,
        SETTINGS.getDefaultPathFormat(Type.Video)) """
    SETTINGS.save()


def changeQualitySettings():
    Printf.settings()
    SETTINGS.audioQuality = AudioQuality(
        int(Printf.enterLimit(LANG.select.CHANGE_AUDIO_QUALITY,
                              LANG.select.MSG_INPUT_ERR,
                              ['0', '1', '2', '3', '4'])))
    """ SETTINGS.videoQuality = VideoQuality(
        int(Printf.enterLimit(LANG.select.CHANGE_VIDEO_QUALITY,
                              LANG.select.MSG_INPUT_ERR,
                              ['1080', '720', '480', '360']))) """
    SETTINGS.save()


def changeSettings():
    Printf.settings()
    SETTINGS.showProgress = Printf.enterBool(LANG.select.CHANGE_SHOW_PROGRESS)
    SETTINGS.showTrackInfo = Printf.enterBool(LANG.select.CHANGE_SHOW_TRACKINFO)
    SETTINGS.checkExist = Printf.enterBool(LANG.select.CHANGE_CHECK_EXIST)
    SETTINGS.includeEP = Printf.enterBool(LANG.select.CHANGE_INCLUDE_EP)
    SETTINGS.saveCovers = Printf.enterBool(LANG.select.CHANGE_SAVE_COVERS)
    SETTINGS.saveAlbumInfo = Printf.enterBool(LANG.select.CHANGE_SAVE_ALBUM_INFO)
    #SETTINGS.downloadVideos = Printf.enterBool(LANG.select.CHANGE_DOWNLOAD_VIDEOS)
    SETTINGS.lyricFile = Printf.enterBool(LANG.select.CHANGE_ADD_LRC_FILE)
    SETTINGS.multiThread = Printf.enterBool(LANG.select.CHANGE_MULITHREAD_DOWNLOAD)
    SETTINGS.usePlaylistFolder = Printf.enterBool(LANG.select.SETTING_USE_PLAYLIST_FOLDER + "('0'-No,'1'-Yes):")
    SETTINGS.downloadDelay = Printf.enterBool(LANG.select.CHANGE_USE_DOWNLOAD_DELAY)
    SETTINGS.language = Printf.enter(LANG.select.CHANGE_LANGUAGE + "(" + LANG.getLangChoicePrint() + "):")
    LANG.setLang(SETTINGS.language)
    SETTINGS.save()


def changeApiKey():
    item = apiKey.getItem(SETTINGS.apiKeyIndex)
    ver = apiKey.getVersion()

    Printf.info(f'Current APIKeys: {str(SETTINGS.apiKeyIndex)} {item["platform"]}-{item["formats"]}')
    Printf.info(f'Current Version: {str(ver)}')
    Printf.apikeys(apiKey.getItems())
    index = int(Printf.enterLimit("APIKEY index:", LANG.select.MSG_INPUT_ERR, apiKey.getLimitIndexs()))

    if index != SETTINGS.apiKeyIndex:
        SETTINGS.apiKeyIndex = index
        SETTINGS.save()
        TIDAL_API.apiKey = apiKey.getItem(index)
        return True
    return False


'''
=================================
LOGIN
=================================
'''


def __displayTime__(seconds, granularity=2):
    if seconds <= 0:
        return "unknown"

    result = []
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def loginByWeb():
    try:
        print(LANG.select.AUTH_START_LOGIN)
        # get device code
        url = TIDAL_API.getDeviceCode()

        print(LANG.select.AUTH_NEXT_STEP.format(
            aigpy.cmd.green(url),
            aigpy.cmd.yellow(__displayTime__(TIDAL_API.key.authCheckTimeout))))
        print(LANG.select.AUTH_WAITING)

        start = time.time()
        elapsed = 0
        while elapsed < TIDAL_API.key.authCheckTimeout:
            elapsed = time.time() - start
            if not TIDAL_API.checkAuthStatus():
                time.sleep(TIDAL_API.key.authCheckInterval + 1)
                continue

            Printf.success(LANG.select.MSG_VALID_ACCESSTOKEN.format(
                __displayTime__(int(TIDAL_API.key.expiresIn))))

            TOKEN.userid = TIDAL_API.key.userId
            TOKEN.countryCode = TIDAL_API.key.countryCode
            TOKEN.accessToken = TIDAL_API.key.accessToken
            TOKEN.refreshToken = TIDAL_API.key.refreshToken
            TOKEN.expiresAfter = time.time() + int(TIDAL_API.key.expiresIn)
            TOKEN.save()
            return True

        raise Exception(LANG.select.AUTH_TIMEOUT)
    except Exception as e:
        Printf.err(f"Login failed.{str(e)}")
        return False


def loginByConfig():
    try:
        if aigpy.string.isNull(TOKEN.accessToken):
            return False

        if TIDAL_API.verifyAccessToken(TOKEN.accessToken):
            Printf.info(LANG.select.MSG_VALID_ACCESSTOKEN.format(
                __displayTime__(int(TOKEN.expiresAfter - time.time()))))

            TIDAL_API.key.countryCode = TOKEN.countryCode
            TIDAL_API.key.userId = TOKEN.userid
            TIDAL_API.key.accessToken = TOKEN.accessToken
            return True

        Printf.info(LANG.select.MSG_INVALID_ACCESSTOKEN)
        if TIDAL_API.refreshAccessToken(TOKEN.refreshToken):
            Printf.success(LANG.select.MSG_VALID_ACCESSTOKEN.format(
                __displayTime__(int(TIDAL_API.key.expiresIn))))

            TOKEN.userid = TIDAL_API.key.userId
            TOKEN.countryCode = TIDAL_API.key.countryCode
            TOKEN.accessToken = TIDAL_API.key.accessToken
            TOKEN.expiresAfter = time.time() + int(TIDAL_API.key.expiresIn)
            TOKEN.save()
            return True
        else:
            TokenSettings().save()
            return False
    except Exception as e:
        return False


def loginByAccessToken():
    try:
        print("-------------AccessToken---------------")
        token = Printf.enter("accessToken('0' go back):")
        if token == '0':
            return
        TIDAL_API.loginByAccessToken(token, TOKEN.userid)
    except Exception as e:
        Printf.err(str(e))
        return

    print("-------------RefreshToken---------------")
    refreshToken = Printf.enter("refreshToken('0' to skip):")
    if refreshToken == '0':
        refreshToken = TOKEN.refreshToken

    TOKEN.accessToken = token
    TOKEN.refreshToken = refreshToken
    TOKEN.expiresAfter = 0
    TOKEN.countryCode = TIDAL_API.key.countryCode
    TOKEN.save()
