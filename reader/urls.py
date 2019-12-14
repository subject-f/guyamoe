from django.urls import path, re_path
from api.api import all_chapter_data_etag, chapter_data_etag
from reader import views
from django.views.decorators.http import condition
from reader.feed import AllChaptersFeed, SeriesChaptersFeed
from reader.models import Chapter

urlpatterns = [
    re_path(r'^manga/(?P<series_slug>[\w-]+)/$', views.series_info, name='reader-manga'),
    re_path(r'^series/(?P<series_slug>[\w-]+)/$', views.series_info, name='reader-series'),
    re_path(r'^manga/(?P<series_slug>[\w-]+)/admin$', views.series_info_admin, name='reader-manga-admin'),
    re_path(r'^series/(?P<series_slug>[\w-]+)/admin$', views.series_info_admin, name='reader-series-admin'),
     re_path(r'^manga/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})$', views.reader, name='reader-manga-chapter'),
     re_path(r'^series/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})$', views.reader, name='reader-series-chapter'),
    re_path(r'^md_proxy/(?P<md_series_id>[\d]{1,9})/$', views.md_proxy, name='reader-md-proxy'),
    re_path(r'^md_proxy/(?P<md_series_id>[\d]{1,9})/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})$', views.md_chapter, name='reader-md-chapter'),
    re_path(r'^update_view_count/', views.hit_count, name='reader-view-count'),
    re_path(r'^other/rss/all$', condition(etag_func=all_chapter_data_etag)(AllChaptersFeed())),
    path(r'other/rss/<str:series_slug>', condition(etag_func=chapter_data_etag)(SeriesChaptersFeed())),
]
