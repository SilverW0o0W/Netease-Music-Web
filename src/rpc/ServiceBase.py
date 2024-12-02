#!/usr/bin/env python
# coding=utf-8

import sys

from constants import EXPORT_LYRIC_TYPE_ORIGIN, EXPORT_LYRIC_TYPE_TRANSLATED, EXPORT_LYRIC_TYPE_MIX

sys.path.append("../")


class ServiceBase(object):
    lyric_type_map = {
        EXPORT_LYRIC_TYPE_ORIGIN: ("lyric",),
        EXPORT_LYRIC_TYPE_TRANSLATED: ("translated_lyric", "lyric",),
        EXPORT_LYRIC_TYPE_MIX: ("lyric", "translated_lyric",),
    }

    def __init__(self, dao, conf):
        self.dao = dao
