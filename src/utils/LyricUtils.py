#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-

import re
import datetime


def merge_lyric(lyric, t_lyric):
    l1, d1 = analysis_lyric(lyric)
    l2, d2 = analysis_lyric(t_lyric)

    text = []
    all = []
    all.extend(l1)
    all.extend(l2)
    all = list(set(all))
    all.sort()

    for s in all:
        s_in_1 = False
        if s in d1:
            s_in_1 = True
            text.append("{}{}".format(
                "[{}]".format(datetime.datetime.fromtimestamp(s).strftime("%M:%S.%f")[:-3]),
                d1[s]
            ))
        if s in d2:
            s2 = s + 0.001 if s_in_1 else s
            text.append("{}{}".format(
                "[{}]".format(datetime.datetime.fromtimestamp(s2).strftime("%M:%S.%f")[:-3]),
                d2[s]
            ))

    return "\n".join(text)


lrc_time_pattern = r"^\[\d{2}:\d{2}(\.\d{1,3})?\]"


def analysis_lyric(lyric):
    lyric_dict = {}
    lyric_time = set()
    for line in lyric.split("\n"):
        match = re.match(lrc_time_pattern, line)
        if not match:
            continue
        start, end = match.span()
        time_str = line[start + 1:end - 1]
        fmt = "%M:%S.%f" if "." in time_str else "%M:%S"
        dt = datetime.datetime.strptime(time_str, fmt)
        timestamp = dt.timestamp()
        lyric_time.add(timestamp)
        lyric_dict[timestamp] = line[end:]
    return list(lyric_time), lyric_dict
