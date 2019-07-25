#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-


def bytes_to_str(value):
    return value.decode('utf-8', 'ignore') if isinstance(value, bytes) else value
