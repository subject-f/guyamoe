from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='site-home'),
    path('admin_home', views.admin_home, name='admin_home'),
    path('about/', views.about, name='site-about'),
]
