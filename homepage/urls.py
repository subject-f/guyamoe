from django.urls import path, re_path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='site-home'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('about/', views.about, name='site-about'),
    re_path(r'^(?P<chapter>[\d-]*)/$', views.main_series_chapter, name='site-main-series-chapter'),
    re_path(r'^(?P<chapter>[\d-]*)/(?P<page>\d*)/$', views.main_series_page, name='site-main-series-page'),
    path('latest/', views.latest, name='site-main-series-latest')
]
