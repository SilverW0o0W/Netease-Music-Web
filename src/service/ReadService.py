#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

sys.path.append("../")

import time
from service import ServiceBase

from cloudmusic.spider import utils


class ReadService(ServiceBase):

    def read_song(self, params):
        song_id = params.get("song_id", None)
        if not song_id:
            url = params.get("url", "")
            song_id = utils.match_song(url)
        if not song_id:
            return False, "", {}

        lrc_type = int(self.body_params.get('type', 0))
        name = ''
        if real_type == 0:
            status, msg, path = Export.export_song(real_id, lrc_type=lrc_type)
            name = Reader.get_file_name(real_id, name_format=name_format)
        elif real_type == 1:
            Reader.get_playlist(real_id, name_format=name_format)

    def get_db_song(self,song_id):