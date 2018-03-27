from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^detail$', views.detail_action, name='detail_action'),
    url(r'^lyric/song$', views.export_song_action, name='export_song_action'),
    url(r'^lyric/playlist$', views.export_playlist_action, name='export_playlist_action'),
]
