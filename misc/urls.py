from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.misc_pages, name="misc-all-pages"),
    re_path(r"^(?P<page_url>[\w-]+)/$", views.content, name="misc-page"),
    path("api/update_view_count/", views.hit_count, name="page-view-count"),
]
