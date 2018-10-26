#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import os
import json
import time
import alchemy

from cloudmusic.spider.api import request_song
from cloudmusic.spider.adapter import adapt_song


class Song(object):
    name_format_map = {
        '0': '{name}',
        '1': '{artists} - {name}',
        '2': '{name} - {artists}',
    }

    def __init__(self):
        pass

    def get_file_name(self, song_id, name_format='0'):
        content = request_song(song_id)
        song = adapt_song(content, song_id)

        artists_list = [artist.name for artist in song.artists]
        artists = ','.join(artists_list)
        return self.name_format_map.get(name_format, '').format(
            name=song.name, artists=artists
        )

        # now = int(time.time())
        # db_song = alchemy.Song(
        #     origin_id=song_id,
        #     name=song.name,
        #     artists=artists_name,
        #     created_time=now,
        #     updated_time=now
        # )
        # db_song.merge()
