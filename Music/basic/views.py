# coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
import json
from info_collector import InfoCollector
from lyric_exporter import LyricExporter

collector = InfoCollector()


# Create your views here.
def index(request):
    context = {
    }
    return render(request, 'music/index.html', context)


def detail_action(request):
    url = request.POST.get('url', None)
    if not url:
        context = {
            'alert': "Url Invalid!",
        }
        return render(request, 'music/index.html', context)
    context = collector.request_url(url)
    if not context:
        pass
    return HttpResponse(json.dumps(context, ensure_ascii=False), content_type="application/json")


download_path = 'basic/lyric'
lyric_dir = str.format('{0}/song/', download_path)
playlist_dir = str.format('{0}/playlist/', download_path)


def export_action(request):
    url = request.POST.get('id', None)
    if not url:
        context = {
        }
        return render(request, 'music/index.html', context)
    url_type = request.POST.get('type', 'song')
    format = request.POST.get('format', '1')
    format_dict = {
        '1': '{1}',
        '2': '{0} - {1}',
        '3': '{1} - {0}',
    }
    name_format = format_dict[format]
    exporter = LyricExporter(lyric_dir, name_format=name_format)
    file_name = exporter.get_song(url) if url_type == 'song' else exporter.get_playlist(url, playlist_dir)
    file_stream = open(file_name[1], 'rb')
    response = FileResponse(file_stream)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = str.format('attachment;filename={0}', file_name[0])
    return response


def export_song_action(request):
    song_id = request.POST.get('id', None)
    if not song_id:
        context = {
        }
        return render(request, 'music/index.html', context)
    format = request.POST.get('format', '1')
    format_dict = {
        '1': '{1}',
        '2': '{0} - {1}',
        '3': '{1} - {0}',
    }
    name_format = format_dict[format]
    exporter = LyricExporter(lyric_dir, name_format=name_format)
    file_name = exporter.export(song_id)
    file_stream = open(file_name[1], 'rb')
    response = FileResponse(file_stream)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = str.format('attachment;filename={0}', file_name[0])
    return response


def export_playlist_action(request):
    playlist_id = request.POST.get('id', None)
    if not playlist_id:
        context = {
        }
        return render(request, 'music/index.html', context)
    format = request.POST.get('format', '1')
    format_dict = {
        '1': '{1}',
        '2': '{0} - {1}',
        '3': '{1} - {0}',
    }
    name_format = format_dict[format]
    exporter = LyricExporter(lyric_dir, name_format=name_format)
    file_name = exporter.export_playlist(playlist_id, playlist_dir=playlist_dir)
    file_stream = open(file_name[1], 'rb')
    response = FileResponse(file_stream)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = str.format('attachment;filename={0}', file_name[0])
    return response
