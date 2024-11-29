#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@author: 
@create: 2024/11/29
@brief:
"""

import g
import json
from constants import const
from utils import BaseUtils


def get_json_cache(redis_obj, key):
    try:
        value = redis_obj.get(key)
        value = BaseUtils.bytes_to_str(value)
    except Exception:
        value = ""
    json_obj = json.loads(value) if value else {}
    return json_obj


def set_json_cache(redis_obj, key, lyric):
    value = json.dumps(lyric)
    redis_obj.set(key, value, ex=const.CACHE_TTL)


def get_song_cache(song_id):
    key = const.KEY_SONG.format(song_id=song_id)
    return get_json_cache(g.MusicCache, key)


def set_song_cache(song_id, song):
    key = const.KEY_SONG.format(song_id=song_id)
    set_json_cache(g.MusicCache, key, song)


def get_lyric_cache(song_id):
    key = const.KEY_LYRIC.format(song_id=song_id)
    return get_json_cache(g.MusicCache, key)


def set_lyric_cache(song_id, lyric):
    key = const.KEY_LYRIC.format(song_id=song_id)
    set_json_cache(g.MusicCache, key, lyric)
