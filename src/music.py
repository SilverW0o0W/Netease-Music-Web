#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-


import os
import sys
import json
import traceback
import copy

import toml
import redis

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.template

from rpc.lyric import Exporter
from rpc.ReadService import ReadService
from dao.alchemy import DBWorker

Reader = None
Export = None
gReadService = None


class HandlerBase(tornado.web.RequestHandler):
    pass


class ViewBase(HandlerBase):
    def view_base(self, relative_url):
        self.render(relative_url)


class APIBase(HandlerBase):

    def post_base(self, func, error_msg="内部错误"):
        resp = {
            "status": -1,
            "user_msg": ""
        }
        _params = None
        try:
            _params = json.loads(self.request.body)
            params = copy.deepcopy(_params)
            status, msg, data = func(params)
            if status == 0:
                resp["data"] = data
            else:
                resp["user_msg"] = msg
                resp["_user_msg"] = msg
            resp["status"] = status
        except Exception:
            resp["user_msg"] = error_msg
            resp["_user_msg"] = traceback.format_exc()
        resp.pop("_user_msg", "")
        self.write(json.dumps(resp))


class FileBase(HandlerBase):
    def get_base(self, file_name, value, func=None):
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=%s' % file_name)
        func = func or self.write_from_str
        func(value)
        self.finish()

    def write_from_file(self, path):
        with open(path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)

    def write_from_str(self, value):
        self.write(value)


class MainHandler(ViewBase):
    def get(self):
        self.view_base("views/templates/main.html")


class Lyric(ViewBase):
    def get(self):
        self.view_base("views/templates/lyric.html")


class APISong(APIBase):
    def post(self, *args, **kwargs):
        self.post_base(gReadService.read_song, error_msg="内部错误")


class APILyric(APIBase):
    def post(self, *args, **kwargs):
        self.post_base(gReadService.read_lyric, error_msg="内部错误")


class FileLyric(FileBase):
    def get(self, *args, **kwargs):
        gReadService.read_lyric_file()
        self.get_base(file_name, value)


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
    song_db = DBWorker(Config["CONNECT_STRING"])
    Export = Exporter(lyric_cache, Config["DOWNLOAD_DIR"], Config["CACHE_DIR"])
    create_path([Config["DOWNLOAD_DIR"], Config["CACHE_DIR"]])
    gReadService = ReadService(song_db, Config)

    app = tornado.web.Application(
        [
            (r"/lyric", Lyric),

            (r"/api/song", APISong),
            # (r"/api/playlist/detail", PlaylistDetail),

            (r"/api/lyric", APILyric),

            (r"/file/lyric", FileLyric),

            (r"/", MainHandler),
            (r"/views/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "views")}),
        ],
    )

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.current().start()
