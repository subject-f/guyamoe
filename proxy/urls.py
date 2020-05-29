from django.urls import path, re_path
from django.views.decorators.http import condition
from reader.models import Chapter
from . import sources
from django.urls import path, include

urlpatterns = [
    path("api/", include([route for source in sources for route in source.register_api_routes()])),
    path("", include([route for source in sources for route in source.register_frontend_routes()])),
]
