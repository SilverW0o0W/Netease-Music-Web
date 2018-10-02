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


class WebBase(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.body:
            try:
                self.params = json.loads(self.request.body)
            except:
                self.params = {}


class Lyric(WebBase):
    def get(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("%s port /path/to/config_file" % (sys.argv[0]))
        exit(1)
    if not os.path.isfile(sys.argv[2]):
        print("config file %s not exist" % (sys.argv[2]))
        exit(1)
    with open(sys.argv[2], "r") as f:
        Config = toml.load(f)

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/views/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "views")}),
        ],
        debug=True,
    )

    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.current().start()
