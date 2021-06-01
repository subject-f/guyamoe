from django.urls import path, re_path
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control

from api.api import all_chapter_data_etag, chapter_data_etag
from reader import views
from reader.feed import AllChaptersFeed, SeriesChaptersFeed
from reader.models import Chapter

urlpatterns = [
    re_path(
        r"^manga/(?P<series_slug>[\w-]+)/$", views.series_info, name="reader-manga"
    ),
    re_path(
        r"^series/(?P<series_slug>[\w-]+)/$", views.series_info, name="reader-series"
    ),
    re_path(
        r"^manga/(?P<series_slug>[\w-]+)/admin$",
        views.series_info_admin,
        name="reader-manga-admin",
    ),
    re_path(
        r"^series/(?P<series_slug>[\w-]+)/admin$",
        views.series_info_admin,
        name="reader-series-admin",
    ),
    re_path(
        r"^manga/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/$",
        views.reader,
        name="reader-manga-chapter-shortcut",
    ),
    re_path(
        r"^series/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/$",
        views.reader,
        name="reader-series-chapter-shortcut",
    ),
    re_path(
        r"^manga/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})/$",
        views.reader,
        name="reader-manga-chapter",
    ),
    re_path(
        r"^series/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})/$",
        views.reader,
        name="reader-series-chapter",
    ),
    re_path(r"^update_view_count/", views.hit_count, name="reader-view-count"),
    re_path(
        r"^other/rss/all$",
        cache_control(
            public=True, max_age=600, s_maxage=600
        )(  # Cache control for CF, etag for RSS readers
            condition(etag_func=all_chapter_data_etag)(AllChaptersFeed())
        ),
    ),
    path(
        r"other/rss/<str:series_slug>",
        cache_control(public=True, max_age=600, s_maxage=600)(
            condition(etag_func=chapter_data_etag)(SeriesChaptersFeed())
        ),
    ),
]
