#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

sys.path.append("../")

import time
from service import ServiceBase

from cloudmusic.spider import utils
from cloudmusic.spider.api import request_song, request_playlist
from cloudmusic.spider.adapter import adapt_song, adapt_playlist


class ReadService(ServiceBase):

    def read_song(self, params):
        song_id = params.get("song_id", None)
        url = params.get("url", "")
        song_id = utils.match_song(url) if not song_id else song_id
        if not song_id:
            return False, "", {}
        self.get_song(song_id)

    def get_song(self, song_id):
        db_song = self.song_db.query_song(song_id)
        if db_song:
            name = db_song.name
            artists = db_song.artists
        else:
            content = request_song(song_id)
            song = adapt_song(content, song_id)
            name = song.name
            artists_list = [artist.name for artist in song.artists]
            artists = ','.join(artists_list)
            db_song = alchemy.Song(
                origin_id=song_id,
                name=song.name,
                artists=artists,
            )
            self.song_db.merge_song(db_song)
        return {
            'id': song_id,
            'name': name,
            'artists': artists,
        }
