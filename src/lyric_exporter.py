#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import os
import json

from cloudmusic.spider.api import request_lyric

ORIGIN = 0
TRANS = 1
MERGE = 2


class Exporter(object):

    def __init__(self, lyric_cache):
        self.lyric_cache = lyric_cache

    def get_cache_path(self, song_id):
        key = 'lyric:song:{}'.format(song_id)
        try:
            value = self.lyric_cache.get(key)
        except Exception as e:
            return False, str(e), None
        return True, "", value

    def get_cache_file(self, song_id, lrc_type):
        key = 'lyric:song:{0}:{1}'.format(song_id, lrc_type)
        try:
            value = self.lyric_cache.get(key)
        except Exception as e:
            return False, str(e), None
        return True, "", value

    def download(self, song_id):
        lyric_data = request_lyric(song_id)
        status, data = self.adapt_lyric(lyric_data)
        if not status:
            return False, '', None
        key = 'lyric:song:{}'.format(song_id)
        json_path = "{}.json".format(song_id)
        with open(json_path, "w") as f:
            f.write(json.dump(data))
        self.lyric_cache.set(key, json_path)
        return True, json_path, data

    @staticmethod
    def adapt_lyric(lyric_data):
        lyric = {}
        _lrc = lyric_data.get('lyric', '')
        _t_lrc = lyric_data.get('tlyric', '')
        if not _lrc and not _t_lrc:
            return False, None
        if _lrc:
            lyric['lyric'] = _lrc
        if _t_lrc:
            lyric['trans_lyric'] = _lrc
        return True, lyric

    def export(self, song_id):
        status, msg, path = self.get_cache_path(song_id)
        if not (status and os.path.isfile(path)):
            status, path, lyric_data = self.download(song_id)
        if not status:
            return None
        with open(path, "r") as f:
            lyric_data = json.load(f)
        return lyric_data

    def export_lyric(self, song_id, lrc_type=None):
        lrc_type = ORIGIN if lrc_type is None else lrc_type
        key = 'lyric:song:{0}:{1}'.format(song_id, lrc_type)
        status, msg, lrc_path = self.get_cache_file(song_id, lrc_type)
        if status and os.path.isfile(lrc_path):
            return True, "", lrc_path
        lrc_data = self.export(song_id)
        lrc_text = ""
        if lrc_type == ORIGIN:
            lrc_text = lrc_data.get("lyric", "")
        elif lrc_type == TRANS:
            lrc_text = lrc_data.get("trans_lyric", "")
            lrc_text = lrc_text if lrc_text else lrc_data.get("lyric", "")
        elif lrc_type == MERGE:
            lrc_text1 = lrc_data.get("lyric", "")
            lrc_text2 = lrc_data.get("trans_lyric", "")
            lrc_text = lrc_text1 + lrc_text2
        if not lrc_text:
            return False, "lrc not found", ""
        lrc_path = "{0}_{1}.lrc".format(song_id, lrc_type)
        with open(lrc_path, "w") as f:
            f.write(lrc_text)
        self.lyric_cache.set(key, lrc_path)
        return True, "", lrc_path
