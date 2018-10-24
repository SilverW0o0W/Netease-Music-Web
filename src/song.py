#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import os
import json
import time
import alchemy

from cloudmusic.spider.api import request_song
from cloudmusic.spider.adapter import adapt_song


class Song(object):
    def __init__(self):
        pass

    def get_file_name(self, song_id, name_format=0):
        content = request_song(song_id)
        song = adapt_song(content, song_id)
        name_list = [artist.name for artist in song.artists]
        artists_name = ','.join(name_list)

        now = int(time.time())
        db_song = alchemy.Song(
            origin_id=song_id,
            name=song.name,
            artists=artists_name,
            created_time=now,
            updated_time=now
        )
        db_song.merge()
