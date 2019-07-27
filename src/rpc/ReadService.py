#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

sys.path.append("../")

import time
import json

from voluptuous import MultipleInvalid

from cloudmusic.spider import utils as music_utils

import g
from constants import const

from rpc import schema
from rpc.ServiceBase import ServiceBase

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
            self.fill_lyric_data(lyric)
            return 0, "", lyric
        song = NEUtils.get_song(song_id)
        if not song:
            return -2, "获取歌曲信息失败", {}
        status, lyric = NEUtils.get_lyric(song_id)
        available = True if lyric else False

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
                "available": available,
                "lyric": lyric.get("lyric", ""),
                "translated_lyric": lyric.get("trans_lyric", ""),
            },
        }

        key = const.LYRIC_KEY.format(song_id)
        g.MusicCache.setex(key, const.CACHE_TTL, json.dumps(data))
        self.fill_lyric_data(data)

        return 0, "", data

    @staticmethod
    def fill_lyric_data(lyric):
        lyric["lyric"]["download"] = "file/lyric?id={}".format(lyric["id"])

    def download_lyric(self, params):
        try:
            schema.download_lyric_schema(params)
        except MultipleInvalid as e:
            return 400, "参数错误", ""
        song_id = int(params["id"])
        lrc_format = int(params["format"])
        lrc_type = int(params["type"])
        lyric = LyricUtils.get_lyric(song_id)
        if not lyric:
            return 404, "资源不存在", ""

        name = lyric["name"]
        artists = self.get_str_artists(lyric, lrc_format)

        file_name = self.name_format_map[lrc_format].format(
            name=name, artists=artists
        )
        data = {
            "name": file_name + ".lrc",
            "lyric": self.get_lyric_content(lyric, lrc_type),
        }

        return 200, "", data

    @staticmethod
    def get_str_artists(data, lrc_format):
        if lrc_format == 0:
            return ""
        else:
            return ','.join(map(lambda artist: artist["name"], data["artists"]))

    @classmethod
    def get_lyric_content(cls, data, lrc_type):
        lyric = data.get("lyric", {})
        if not lyric:
            return ""
        if lrc_type == 2:
            lyric_content = lyric.get("lyric", "")
            tlyric_content = lyric.get("translated_lyric", "")
            if lyric_content and tlyric_content:
                return LyricUtils.merge_lyric(lyric_content, tlyric_content)
            lrc_type = 1

        if lrc_type in {0, 1}:
            content_fields = cls.lyric_type_map[lrc_type]
            for field in content_fields:
                content = lyric.get(field, "")
                if content:
                    return content

        return ""

    def read_playlist(self, params):
        pass
