#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from cloudmusic.spider.api import request_song, request_playlist
from cloudmusic.spider.adapter import adapt_song, adapt_playlist


def get_song(song_id):
    content = request_song(song_id)
    song = adapt_song(content, song_id)
    name = song.name
    artists = [artist.name for artist in song.artists]
    return {
        'id': song_id,
        'name': name,
        'artists': artists,
    }
