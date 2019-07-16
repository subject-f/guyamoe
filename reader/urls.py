from django.urls import path, re_path
from reader import views

urlpatterns = [
    re_path(r'^series/(?P<series_slug>[\w-]+)/$', views.series_info, name='reader-series'),
    re_path(r'^series/(?P<series_slug>[\w-]+)/admin$', views.series_info_admin, name='reader-series-admin'),
    re_path(r'^series/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})', views.reader, name='reader-chapter'),
    re_path(r'^update_view_count/', views.hit_count, name='reader-view-count'),
]
