#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

sys.path.append("../")

import time
from rpc.ServiceBase import ServiceBase

from cloudmusic.spider import utils as music_utils
from utils import NEUtils


class ReadService(ServiceBase):

    def read_song(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return False, "", {}
        song = NEUtils.get_song(song_id)
        if not song:
            return -2, "获取失败", {}
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
            return False, "", {}
        status, lyric = NEUtils.get_lyric(song_id)
        if not status or not lyric:
            return -2, "", {}
        data = {
            "id": song_id,
            "lyric": lyric.get("lyric", ""),
            "translated_lyric": lyric.get("trans_lyric", "")
        }
        return 0, "", data
