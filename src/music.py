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
from lyric import Exporter

Export = None


class WebBase(tornado.web.RequestHandler):
    def prepare(self):
        self.body_params = {}
        if self.request.body:
            try:
                self.body_params = json.loads(self.request.body)
            except:
                self.body_params = {}


class MainHandler(WebBase):
    def get(self):
        self.render("views/templates/main.html")


class LyricHandler(WebBase):
    def get(self):
        self.render("views/templates/lyric.html")


class SongLyric(WebBase):
    def get(self, *args, **kwargs):
        file_path = self.body_params.get('path', "")
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_path)
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)
        self.finish()

    def post(self, *args, **kwargs):
        song_id = self.body_params.get('id', '')
        if not song_id:
            resp = {
                "status": -1,
                "msg": "请输入song id"
            }
            self.write(json.dumps(resp))
            return
        lrc_type = int(self.body_params.get('type', 0))
        status, msg, path = Export.export_song(song_id, lrc_type=lrc_type)
        resp = {
            "status": status,
            "msg": msg,
            "name": "",
            "path": path,
        }
        self.write(json.dumps(resp))


def create_path(paths):
    for path in paths:
        if not os.path.isdir(path):
            os.makedirs(path)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("%s port /path/to/config_file" % (sys.argv[0]))
        exit(1)
    if not os.path.isfile(sys.argv[2]):
        print("config file %s not exist" % (sys.argv[2]))
        exit(1)
    with open(sys.argv[2], "r") as f:
        Config = toml.load(f)
    lyric_cache = redis.StrictRedis(**Config["LYRIC_CACHE"])
    Export = Exporter(lyric_cache, Config["DOWNLOAD_DIR"], Config["CACHE_DIR"])
    create_path([Config["DOWNLOAD_DIR"], Config["CACHE_DIR"]])

    app = tornado.web.Application(
        [
            (r"/lyric", LyricHandler),
            (r"/lyric/song", SongLyric),

            (r"/", MainHandler),
            (r"/views/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "views")}),
        ],
        debug=True,
    )

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.current().start()
