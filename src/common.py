#!/usr/bin/env python
# coding=utf-8

import toml

global Config
Config = None


def init(config_file):
    global Config
    with open(config_file, "r") as file:
        Config = toml.load(file)
