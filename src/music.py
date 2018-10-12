#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-


import os
import sys
import json

import toml

import tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.template
from tornado.log import access_log

import redis
from lyric import Lyric

LYRIC_CACHE = None


class WebBase(tornado.web.RequestHandler):
    pass


class SongLyric(WebBase):
    def post(self, *args, **kwargs):
        song_id = self.get_argument('id', default='')
        lrc_type = self.get_argument('lrc_type', default=None)
        if not song_id:
            resp = {
                "status": -1,
                "msg": "请输入song id"
            }
            self.write(json.dumps(resp))
            return
        lyric = Lyric(LYRIC_CACHE)
        status, msg, path = lyric.export_song(song_id, lrc_type=lrc_type)
        resp = {
            "status": status,
            "msg": msg,
            "path": path,
        }
        self.write(json.dumps(resp))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("%s port /path/to/config_file" % (sys.argv[0]))
        exit(1)
    if not os.path.isfile(sys.argv[2]):
        print("config file %s not exist" % (sys.argv[2]))
        exit(1)
    with open(sys.argv[2], "r") as f:
        Config = toml.load(f)
    LYRIC_CACHE = redis.StrictRedis(**Config["LYRIC_CACHE"])

    app = tornado.web.Application(
        [
            (r"/lyric/song", SongLyric),
            (r"/views/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "views")}),
        ],
        debug=True,
    )

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.current().start()
