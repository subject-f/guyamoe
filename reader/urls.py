from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^series/(?P<series_slug>[\w-]+)/(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})', views.reader, name='reader-chapter'),
]
