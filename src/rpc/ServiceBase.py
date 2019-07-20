#!/usr/bin/env python
# coding=utf-8

import sys

sys.path.append("../")

from constants import const


class ServiceBase(object):

    def __init__(self, dao, conf):
        self.dao = dao
