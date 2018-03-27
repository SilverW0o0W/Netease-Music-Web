# coding=utf-8
"""
Download lyric
"""
import os
import sys
from spider import music_utils as utils
from spider import music_adapter as adapter
from spider.music_spider import MusicSpider
from models import Lyric
import zipfile

reload(sys)
sys.setdefaultencoding('utf8')


class LyricExporter(object):
    """
    Crawl song lyric and export to file.
    export_dir: The lyric export folder path.
        default: current directory.
    name_format: The format of export file name.
        {0} is artist name.
        {1} is song name.
        default: '{0} - {1}'.
    """

    extension_name = '{0}.lrc'
    name_format = '{0} - {1}'

    def __init__(self, export_dir=None, name_format=name_format, need_info=True):
        self.export_dir = export_dir
        self.name_format = name_format
        self.need_info = need_info
        self.spider = MusicSpider()

    def generate_model(self, song_info, export_path):
        """
        Concat lyric file name and export dir path.
        """
        is_first = True
        for artist in song_info.artists[1]:
            if is_first:
                artists_name = artist
                is_first = False
            else:
                artists_name += ',' + artist
        artists_name = artists_name.decode('utf-8')
        song_name = song_info.song_name.decode('utf-8')
        concat_name = str.format(self.name_format, artists_name, song_name)
        file_name = str.format(self.extension_name, concat_name).decode('utf-8')
        if export_path is not None and export_path.strip() != '':
            export_path = export_path.strip()
            if export_path[-1] != '/' and export_path[-1] != '\\':
                export_path += '/'
            if os.path.isdir(export_path):
                full_name = export_path + file_name
            else:
                try:
                    os.makedirs(export_path)
                    full_name = export_path + file_name
                except OSError, e:
                    print e.message

        full_name = full_name.decode('utf-8')
        lyric_model = Lyric()
        lyric_model.song_id = song_info.song_id
        lyric_model.artists = artists_name
        lyric_model.name = song_name
        lyric_model.locate_path = full_name
        lyric_model.save()
        return file_name, full_name

    def create_file(self, song_lyric, export_path=None):
        """
        Write lyric to file.
        If song info doesn't exist, file name: song_id.lrc
        If song info exists, default file name: artists_name[,] - song_name.lrc
        """
        file_name = self.generate_model(song_lyric.info, export_path)
        lyric = song_lyric.lyric
        if not lyric:
            return
        with open(file_name[1], 'w') as lrc_file:
            lyric = lyric.encode('mbcs')
            lrc_file.write(lyric)
            return file_name

    def select_lyric(self, song_id):
        try:
            lyric = Lyric.objects.get(song_id=song_id)
            if not os.path.exists(lyric.locate_path):
                return None
            return lyric
        except Lyric.DoesNotExist:
            return None

    def export(self, song_id, song_info=None, export_dir=None):
        """
        Export song lyric.
        """
        lyric = self.select_lyric(song_id)
        if lyric is not None:
            concat_name = str.format(
                self.name_format, lyric.artists, lyric.name)
            file_name = str.format(self.extension_name, concat_name)
            return file_name, lyric.locate_path
        export_dir = self.export_dir if not export_dir else export_dir
        if not song_info:
            if self.need_info:
                info_content = self.spider.request_info(song_id)
                song_info = adapter.adapt_info(song_id, info_content)
        lyric_content = self.spider.request_lyric(song_id)
        song_lyric = adapter.adapt_lyric(song_id, lyric_content, song_info)
        file_name = self.create_file(song_lyric, export_dir)
        return file_name

    def export_songs(self, song_list, export_dir=None):
        """
        Export songs of list
        :param song_list:List of Song object
        :param export_dir:Directory of export path
        :return:Dict of file_name:full_path
        """
        path_dict = {}
        for song in song_list:
            try:
                file_name = self.export(song.song_id, song_info=song.info,
                                        export_dir=export_dir)
                if file_name is not None:
                    path_dict[song.song_id] = file_name
            except BaseException, ex:
                print ex.message
        return path_dict

    def export_playlist(self, playlist_id, export_dir=None, playlist_dir=None):
        """
        Export all songs in playlist
        """
        content = self.spider.request_playlist(playlist_id)
        playlist = adapter.adapt_playlist(playlist_id, content)
        path_dict = self.export_songs(playlist.tracks, export_dir=export_dir)
        zip_name = str.format('{0}.zip', playlist_id)
        zip_real_name = str.format('{0}/{1}', playlist_dir, zip_name)

        if not os.path.isdir(playlist_dir):
            os.makedirs(playlist_dir)

        with zipfile.ZipFile(zip_real_name, 'w') as zip_file:
            for song_id, file_name in path_dict.items():
                short_name = file_name[0].decode('utf-8')
                long_name = file_name[1].decode('utf-8')
                zip_file.write(long_name, short_name, compress_type=zipfile.ZIP_DEFLATED)
        return zip_name, zip_real_name

    def export_url(self, url, playlist=False, export_dir=None):
        """
        Export file(s) from input url.
        """
        url_id = utils.match_playlist_id(url)
        if not url_id:
            if playlist:
                raise ValueError('ID not found')
            else:
                url_id = utils.match_song_id(url)
                is_playlist = False
                if not url_id:
                    raise ValueError('ID not found')
        else:
            is_playlist = True
        if is_playlist:
            return self.export_playlist(url_id, export_dir)
        else:
            return self.export(url_id, export_dir)

    def get_song(self, url):
        song_id = utils.match_song_id(url)
        return self.export(song_id)

    def get_playlist(self, url, playlist_dir):
        playlist_id = utils.match_playlist_id(url)
        return self.export_playlist(playlist_id, playlist_dir=playlist_dir)
