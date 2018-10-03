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
        lyric_json = request_lyric(song_id)
        data = self.adapt_lyric(lyric_json)
        key = 'lyric:song:{}'.format(song_id)
        json_path = "{}.json".format(song_id)
        with open(json_path, "w") as f:
            f.write(json.dump(data))
        self.lyric_cache.set(key, json_path)
        return json_path

    @staticmethod
    def adapt_lyric(lyric_json):
        lyric = {}
        # lyric_json['id'] = lyric_json
        return lyric

    def export(self, song_id):
        status, msg, path = self.get_cache_path(song_id)
        if not (status and os.path.isfile(path)):
            path = self.download(song_id)
        with open(path, "r") as f:
            lyric_data = json.load(f)
        return lyric_data

    def export_lyric(self, song_id, lrc_type):
        key = 'lyric:song:{0}:{1}'.format(song_id, lrc_type)
        status, msg, lrc_path = self.get_cache_file(song_id, lrc_type)
        if status and os.path.isfile(lrc_path):
            return True, "", lrc_path
        lrc_data = self.export(song_id)
        lrc_text = ""
        if lrc_type == ORIGIN:
            lrc_text = lrc_data.get("lyric", "")
        elif lrc_type == TRANS:
            lrc_text = lrc_data.get("t_lyric", "")
            lrc_text = lrc_text if lrc_text else lrc_data.get("lyric", "")
        elif lrc_type == MERGE:
            lrc_text1 = lrc_data.get("lyric", "")
            lrc_text2 = lrc_data.get("t_lyric", "")
            lrc_text = lrc_text1 + lrc_text2
        if not lrc_text:
            return False, "lrc not found", ""
        lrc_path = "{0}_{1}.lrc".format(song_id, lrc_type)
        with open(lrc_path, "w") as f:
            f.write(lrc_text)
        self.lyric_cache.set(key, lrc_path)
        return True, "", lrc_path
