from django.urls import path, re_path
from api import views

urlpatterns = [
    re_path(r'^series/(?P<series_slug>[\w-]+)/', views.series_data, name='api-series_data'),
    re_path(r'^get_groups/(?P<series_slug>[\w-]+)/', views.get_groups, name='api-groups'),
    re_path(r'^upload_new_chapter/(?P<series_slug>[\w-]+)/', views.upload_new_chapter, name='api-chapter-upload'),
    re_path(r'^get_volume_covers/(?P<series_slug>[\w-]+)/', views.get_volume_covers, name='api-get-volume-covers'),
    re_path(r'^search_index/(?P<series_slug>[\w-]+)', views.search_index, name='api-search-index'),
    re_path(r'clear_cache/', views.clear_cache, name='api-clear-cache'),
]
