# coding=utf-8

from spider import music_utils as utils
from spider import music_adapter as adapter
from spider.music_spider import MusicSpider


class InfoCollector(object):

    def __init__(self):
        self.spider = MusicSpider()

    def request_url(self, url):
        url_type = utils.match_type(url)
        if url_type & 0b00010 == 0b00010:
            url_id = utils.match_song_id(url)
            return self.request_song(url_id)
        elif url_type & 0b00100 == 0b00100:
            url_id = utils.match_playlist_id(url)
            return self.request_playlist(url_id)
        else:
            return None

    def request_song(self, song_id):
        content = self.spider.request_song(song_id)
        song = adapter.adapt_song(content, song_id)
        name_list = [artist.name for artist in song.artists]
        artists_name = ','.join(name_list)
        context = {}
        context['song'] = {
            'id': song.song_id,
            'name': song.name,
            'artists': artists_name,
            'album': song.album.name,
        }
        return context

    def request_playlist(self, playlist_id):
        content = self.spider.request_playlist(playlist_id)
        playlist = adapter.adapt_playlist(content, playlist_id)
        context = {}
        context['playlist'] = {
            'id': playlist.playlist_id,
            'name': playlist.name,
            'creator': playlist.creator.nickname,
            'count': playlist.track_count
        }
        return context
