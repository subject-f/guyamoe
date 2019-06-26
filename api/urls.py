from django.urls import path, re_path
from api import views

urlpatterns = [
    re_path(r'^series/(?P<series_slug>[\w-]+)/', views.series_data, name='api-series_data'),
]
