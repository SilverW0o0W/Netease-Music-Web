#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import redis

global Config
Config = None
global MusicCache
MusicCache = None


def init(config):
    global Config
    Config = config
    global MusicCache
    MusicCache = redis.StrictRedis(**config["MUSIC_CACHE"])
