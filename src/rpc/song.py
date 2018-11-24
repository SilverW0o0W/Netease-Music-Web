#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import os
import json
import time
import dao.alchemy as alchemy

from cloudmusic.spider.api import request_song, request_playlist
from cloudmusic.spider.adapter import adapt_song, adapt_playlist


class Song(object):
    name_format_map = {
        '0': '{name}',
        '1': '{artists} - {name}',
        '2': '{name} - {artists}',
    }

    def __init__(self, song_db):
        self.song_db = song_db

    def get_song(self, song_id):
        db_song = self.song_db.query_song(song_id)
        if db_song:
            name = db_song.name
            artists = db_song.artists
        else:
            content = request_song(song_id)
            song = adapt_song(content, song_id)
            now = int(time.time())
            name = song.name
            artists_list = [artist.name for artist in song.artists]
            artists = ','.join(artists_list)
            db_song = alchemy.Song(
                origin_id=song_id,
                name=song.name,
                artists=artists,
                created_time=now,
                updated_time=now
            )
            self.song_db.merge_song(db_song)
        return {
            'id': song_id,
            'name': name,
            'artists': artists,
        }

    def get_playlist(self, playlist_id):
        content = request_playlist(playlist_id)
        playlist = adapt_playlist(content, playlist_id)

    def get_file_name(self, song_id, name_format='0'):
        song = self.get_song(song_id)
        if not song:
            return song_id
        return self.name_format_map.get(name_format, '').format(
            name=song.get('name', ''), artists=song.get('artists', '')
        )
