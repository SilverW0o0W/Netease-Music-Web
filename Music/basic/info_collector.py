# coding=utf-8

from spider import music_utils as utils
from spider import music_adapter as adapter
from spider.music_spider import MusicSpider


class InfoCollector(object):

    def __init__(self):
        self.spider = MusicSpider()

    def request_url(self, url):
        url_type = utils.match_type(url)
        if url_type & 0b001 == 0b001:
            url_id = utils.match_song_id(url)
            return self.request_song(url_id)
        elif url_type & 0b010 == 0b010:
            url_id = utils.match_playlist_id(url)
            return self.request_playlist(url_id)
        else:
            return None

    def request_song(self, song_id):
        content = self.spider.request_info(song_id)
        info = adapter.adapt_info(song_id, content)
        is_first = True
        for artist in info.artists[1]:
            if is_first:
                artists = artist
                is_first = False
            else:
                artists += '/' + artist
        artists = artists.decode('utf-8')
        context = {}
        context['song'] = {
            'id': info.song_id,
            'name': info.song_name,
            'artists': artists,
            'album': info.album_name,
        }
        return context

    def request_playlist(self, playlist_id):
        content = self.spider.request_playlist(playlist_id)
        playlist = adapter.adapt_playlist(playlist_id, content)
        context = {}
        context['playlist'] = {
            'id': playlist.playlist_id,
            'name': playlist.name,
            'creator': playlist.creator.nickname,
            'count': playlist.track_count
        }
        return context
