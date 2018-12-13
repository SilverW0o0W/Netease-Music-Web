#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-


import os
import sys
import json
import traceback

import toml

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.template

import redis
from utils import get_real_id
from rpc.song import Song
from rpc.lyric import Exporter
from dao.alchemy import DBWorker

Reader = None
Export = None


class WebBase(tornado.web.RequestHandler):
    def prepare(self):
        self.body_params = {}
        if self.request.body:
            try:
                self.body_params = json.loads(self.request.body)
            except Exception:
                self.body_params = {}


class MainHandler(WebBase):
    def get(self):
        self.render("views/templates/main.html")


class LyricHandler(WebBase):
    def get(self):
        self.render("views/templates/lyric.html")


class Song(WebBase):
    def post(self, *args, **kwargs):
        resp = {
            "status": -1,
            "user_msg": ""
        }
        try:
            params = self.body_params
            status, msg, data = cReadService.read_song(params)
            if status:
                resp["status"] = 0
                resp["data"] = data
            else:
                resp["msg"] = '数据统计出错'
                resp["_msg"] = msg
        except Exception:
            resp["msg"] = '内部错误'
            resp["_msg"] = traceback.format_exc()
        resp.pop("_user_msg", "")
        self.write(json.dumps(resp))

        url_type = self.body_params.get('url_type', '0')
        url = self.body_params.get('url', '0')
        name_format = self.body_params.get('format', '0')
        if not url:
            resp = {
                "status": -1,
                "msg": "请输入链接"
            }
            self.write(json.dumps(resp))
            return

        real_id, real_type = get_real_id(url, url_type)
        if not real_id or real_type not in [0, 1, 2]:
            resp = {
                "status": -1,
                "msg": "请输入合法链接"
            }
            self.write(json.dumps(resp))
            return

        lrc_type = int(self.body_params.get('type', 0))
        status, msg, path = '', '', ''
        name = ''
        if real_type == 0:
            status, msg, path = Export.export_song(real_id, lrc_type=lrc_type)
            name = Reader.get_file_name(real_id, name_format=name_format)
        elif real_type == 1:
            Reader.get_playlist(real_id, name_format=name_format)
        resp = {
            "status": 0,
            "msg": msg,
            "data": [
                {
                    "name": name,
                    "status": "有效" if status else "无效",
                    "uri": "/lyric/song?uri={}&name={}".format(path, name),
                },
            ]
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
    song_db = DBWorker(Config["CONNECT_STRING"])
    Reader = Song(song_db)
    Export = Exporter(lyric_cache, Config["DOWNLOAD_DIR"], Config["CACHE_DIR"])
    create_path([Config["DOWNLOAD_DIR"], Config["CACHE_DIR"]])

    app = tornado.web.Application(
        [
            (r"/lyric", LyricHandler),
            (r"/song", Song),
            (r"/playlist", Playlist),

            (r"/lyric/song", LyricSong),
            (r"/lyric/playlist", PlaylistSong),

            (r"/", MainHandler),
            (r"/views/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "views")}),
        ],
    )

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.current().start()
