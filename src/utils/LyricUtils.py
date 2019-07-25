#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import json

import g
from constants import const
from utils import BaseUtils


def get_lyric(song_id):
    key = const.LYRIC_KEY.format(song_id)
    try:
        value = g.MusicCache.get(key)
        value = BaseUtils.bytes_to_str(value)
    except Exception:
        value = ""
    lyric = json.loads(value) if value else {}
    return lyric
