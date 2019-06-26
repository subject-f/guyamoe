from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# router = rounters.DefaultRouter()
# router.register(r'item')

urlpatterns = [
    path('', views.home, name='site-home'),
    path('about/', views.home, name='site-about'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG :
#     urlpatterns += patterns('', (
#         r'^static/(?P<path>.*)$',
#         'django.views.static.serve',
#         {'document_root': settings.STATIC_ROOT}
#     ))
