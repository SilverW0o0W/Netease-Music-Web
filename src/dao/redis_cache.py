#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@author: 
@create: 2024/11/29
@brief:
"""

import g
import json
from constants import KEY_SONG, TTL_MUSIC, KEY_LYRIC
from utils import BaseUtils


def get_json_cache(redis_obj, key):
    try:
        value = redis_obj.get(key)
        value = BaseUtils.bytes_to_str(value)
    except Exception:
        value = ""
    json_obj = json.loads(value) if value else {}
    return json_obj


def set_json_cache(redis_obj, key, json_obj, ex=None):
    value = json.dumps(json_obj)
    redis_obj.set(key, value, ex=ex)


def get_song_cache(song_id):
    key = KEY_SONG.format(song_id=song_id)
    return get_json_cache(g.MusicCache, key)


def set_song_cache(song_id, song):
    key = KEY_SONG.format(song_id=song_id)
    set_json_cache(g.MusicCache, key, song, ex=TTL_MUSIC)


def get_lyric_cache(song_id):
    key = KEY_LYRIC.format(song_id=song_id)
    return get_json_cache(g.MusicCache, key)


def set_lyric_cache(song_id, lyric):
    key = KEY_LYRIC.format(song_id=song_id)
    set_json_cache(g.MusicCache, key, lyric, ex=TTL_MUSIC)
