from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path("", views.home, name="site-home"),
    path("admin_home/", views.admin_home, name="admin_home"),
    path("about/", views.about, name="site-about"),
    re_path(
        r"^(?P<chapter>[\d-]{1,9})/$",
        views.main_series_chapter,
        name="site-main-series-chapter",
    ),
    re_path(
        r"^(?P<chapter>[\d-]{1,9})/(?P<page>[\d]{1,9})/$",
        views.main_series_page,
        name="site-main-series-page",
    ),
    path("latest/", views.latest, name="site-main-series-latest"),
    path("random/", views.random, name="site-main-series-random"),
]
