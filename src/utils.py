#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

from cloudmusic.utils import match_song
from cloudmusic.utils import match_playlist
from cloudmusic.utils import match_album

SONG = 0
PLAYLIST = 1
ALBUM = 2


def get_real_id(url, url_type):
    real_id = None
    real_type = None
    if url_type == "0":
        real_id, real_type = match_song(url), SONG
    elif url_type == "1":
        real_id, real_type = match_playlist(url), PLAYLIST
    elif url_type == "2":
        real_id, real_type = match_album(url), ALBUM
    elif url_type == "3":
        real_id, real_type = url, SONG
    elif url_type == "4":
        real_id, real_type = url, PLAYLIST
    elif url_type == "5":
        real_id, real_type = url, ALBUM

    return real_id, real_type
