#!/usr/bin/env python
# coding=utf-8

import sys

sys.path.append("../")

from constants import const


class ServiceBase(object):
    name_format_map = {
        0: '{name}',
        1: '{artists} - {name}',
        2: '{name} - {artists}',
    }

    def __init__(self, dao, conf):
        self.dao = dao
