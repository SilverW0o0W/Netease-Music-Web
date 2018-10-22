#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import os
import json
import sqlalchemy

from cloudmusic.spider.api import request_song
from cloudmusic.spider.adapter import adapt_song


class Song(object):
    def __init__(self):
        pass

    def get_file_name(self, song_id, name_format=0):
        pass
