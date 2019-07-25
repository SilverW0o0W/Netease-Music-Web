#!/usr/bin/env python
# coding=utf-8

from voluptuous import Schema
from voluptuous import Required
from voluptuous import Range
from voluptuous import Optional
from voluptuous import All
from voluptuous import Length
from voluptuous import ALLOW_EXTRA
from voluptuous import Invalid


def to_int(value):
    try:
        return int(value)
    except Exception as e:
        raise Invalid(str(e))


download_lyric_schema = Schema({
    Required("id"): All(to_int, Range(min=1)),
    Optional("format"): All(to_int, Range(min=0, max=2)),
    Optional("type"): All(to_int, Range(min=0, max=2)),
}, extra=ALLOW_EXTRA)
