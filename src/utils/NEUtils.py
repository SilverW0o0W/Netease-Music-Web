#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

from cloudmusic.spider import api as music_api
from cloudmusic.spider import adapter as music_adapter


def get_lyric(song_id):
    lyric_data = music_api.request_lyric(song_id)
    status, lyric = adapt_lyric(lyric_data)
    if not status:
        return False, None
    return True, lyric


def adapt_lyric(lyric_data):
    lyric = {}
    lrcs = {('lrc', 'lyric'), ('tlyric', 'trans_lyric')}
    either_exist = False
    for s_key, d_key in lrcs:
        tmp_lrc = lyric_data.get(s_key, {})
        if tmp_lrc:
            either_exist = True
            lyric[d_key] = tmp_lrc.get('lyric', '')
    return either_exist, lyric


def get_song(song_id):
    content = music_api.request_song(song_id)
    song = music_adapter.adapt_song(content, song_id)
    return song
