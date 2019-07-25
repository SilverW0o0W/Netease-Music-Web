#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

sys.path.append("../")

import time
import json

import g
from constants import const
from rpc.ServiceBase import ServiceBase

from cloudmusic.spider import utils as music_utils
from utils import NEUtils
from utils import LyricUtils


class ReadService(ServiceBase):

    def read_song(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return -2, "参数错误", {}
        song = NEUtils.get_song(song_id)
        if not song:
            return -3, "获取失败", {}
        data = {
            "id": int(song.song_id),
            "name": song.name,
            "album": {
                "id": int(song.album.album_id),
                "name": song.album.name,
            },
            "artists": [
                {
                    "id": int(artist.artist_id),
                    "name": artist.name,
                }
                for artist in song.artists
            ]
        }
        return 0, "", data

    def read_lyric(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return -2, "参数错误", {}
        status, lyric = NEUtils.get_lyric(song_id)
        if not status or not lyric:
            return -3, "", {}
        data = {
            "id": song_id,
            "lyric": lyric.get("lyric", ""),
            "translated_lyric": lyric.get("trans_lyric", "")
        }
        return 0, "", data

    def read_song_lyric(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return -1, "", {}

        lyric = LyricUtils.get_lyric(song_id)
        if lyric:
            return 0, "", lyric
        song = NEUtils.get_song(song_id)
        if not song:
            return -2, "获取歌曲信息失败", {}
        status, lyric = NEUtils.get_lyric(song_id)

        data = {
            "id": song_id,
            "name": song.name,
            "album": {
                "id": int(song.album.album_id),
                "name": song.album.name,
            },
            "artists": [
                {
                    "id": int(artist.artist_id),
                    "name": artist.name,
                }
                for artist in song.artists
            ],
            "lyric": {
                "available": True if lyric else False,
                "lyric": lyric.get("lyric", ""),
                "translated_lyric": lyric.get("trans_lyric", ""),
                "download": "file/lyric?id={}".format(song_id),
            },
        }

        key = const.LYRIC_KEY.format(song_id)
        g.MusicCache.setex(key, const.CACHE_TTL, json.dumps(data))

        return 0, "", data

    def download_lyric(self, song_id):
        lyric = LyricUtils.get_lyric(song_id)
        return "test.lrc", lyric.get("lyric", {}).get("lyric", "")
