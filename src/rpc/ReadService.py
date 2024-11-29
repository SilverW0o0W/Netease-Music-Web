#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

sys.path.append("../")

import json

from voluptuous import MultipleInvalid
from cloudmusic import utils as music_utils

from rpc import schema
from rpc.ServiceBase import ServiceBase

from dao.redis_cache import get_lyric_cache, set_lyric_cache, get_song_cache, set_song_cache

from utils import NEUtils
from utils import LyricUtils


class ReadService(ServiceBase):

    def read_song(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return -2, "参数错误", {}
        song = self.get_and_update_song(song_id)
        if not song:
            return -3, "获取失败", {}
        return 0, "", song

    def read_lyric(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return -2, "参数错误", {}

        lyric = self.get_and_update_lyric(song_id)
        if not lyric:
            return -3, "获取失败", {}
        return 0, "", lyric

    def read_song_lyric(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = music_utils.match_song(url) if not song_id else song_id
        if not song_id:
            return -1, "id匹配失败", {}

        song = self.get_and_update_song(song_id)
        if not song:
            return -2, "获取失败", {}
        lyric = self.get_and_update_lyric(song_id)
        song["lyric"] = {
            "available": lyric["available"] if lyric else True,
            "download": self.get_lyric_download_url(song_id),
        }
        data = {
            "songs": [song, ]
        }
        return 0, "", data

    @staticmethod
    def get_lyric_download_url(song_id):
        return "file/lyric?id={}".format(song_id)

    @classmethod
    def get_and_update_song(cls, song_id):
        song = get_song_cache(song_id)
        if song:
            return song
        _song = NEUtils.get_song(song_id)
        song = {
            "id": int(_song.song_id),
            "name": _song.name,
            "album": {
                "id": int(_song.album.album_id),
                "name": _song.album.name,
            },
            "artists": [
                {
                    "id": int(artist.artist_id),
                    "name": artist.name,
                }
                for artist in _song.artists
            ]
        }
        set_song_cache(song_id, song)
        return song

    @classmethod
    def get_and_update_lyric(cls, song_id):
        lyric = get_lyric_cache(song_id)
        if lyric:
            return lyric
        status, _lyric = NEUtils.get_lyric(song_id)
        if not status:
            return {}
        available = True if _lyric else False
        lyric = {
            "available": available,
            "lyric": "",
            "translated_lyric": "",
        }
        if available:
            lyric["lyric"] = _lyric.get("lyric", "")
            lyric["translated_lyric"] = _lyric.get("trans_lyric", "")
        set_lyric_cache(song_id, lyric)
        return lyric

    def download_lyric(self, params):
        try:
            schema.download_lyric_schema(params)
        except MultipleInvalid as e:
            return 400, "参数错误", {}
        data = {}
        song_id = int(params["id"])
        lrc_format = int(params["format"])
        lrc_type = int(params["type"])
        song = self.get_and_update_song(song_id)
        if not song:
            return 404, "资源不存在", data

        name = song["name"]
        artists = self.get_str_artists(song, lrc_format)

        file_name = self.name_format_map[lrc_format].format(
            name=name, artists=artists
        )
        lyric = self.get_and_update_lyric(song_id)
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
    def get_lyric_content(cls, lyric, lrc_type):
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
