from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='site-home'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('about/', views.about, name='site-about'),
    re_path(r'^title/(?P<md_series_id>[\d]{1,9})/$', views.md_series, name='site-md-series'),
    re_path(r'^title/(?P<md_series_id>[\d]{1,9})/([\w-]+)/$', views.md_series, name='site-md-series'),
    re_path(r'^chapter/(?P<md_chapter_id>[\d]{1,9})/$', views.md_chapter, name='site-md-chapter'),
    re_path(r'^chapter/(?P<md_chapter_id>[\d]{1,9})/(?P<page>[\d]{1,9})/$', views.md_chapter, name='site-md-chapter'),
    re_path(r'^g/(?P<nh_series_id>[\d]{1,9})/$', views.nh_series, name='site-md-chapter'),
    re_path(r'^g/(?P<nh_series_id>[\d]{1,9})/(?P<page>[\d]{1,9})/$', views.nh_series, name='site-md-chapter'),
    re_path(r'^(?P<chapter>[\d-]*)/$', views.main_series_chapter, name='site-main-series-chapter'),
    re_path(r'^(?P<chapter>[\d-]*)/(?P<page>\d*)/$', views.main_series_page, name='site-main-series-page'),
    path('latest/', views.latest, name='site-main-series-latest'),
]
