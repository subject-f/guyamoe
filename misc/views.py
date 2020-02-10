from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.core.cache import cache
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import decorator_from_middleware
import json
import re

from reader.middleware import OnlineNowMiddleware
from reader.models import HitCount
from reader.users_cache_lib import get_user_ip
from .models import Page
from guyamoe.settings import STATIC_VERSION


@csrf_exempt
@decorator_from_middleware(OnlineNowMiddleware)
def hit_count(request):
    if request.method == "POST":
        user_ip = get_user_ip(request)
        page_id = f"url_{request.POST['page_url']}/{user_ip}"
        if not cache.get(page_id):
            cache.set(page_id, page_id, 60)
            page_url = request.POST["page_url"]
            page_id = Page.objects.get(page_url=page_url).id
            page = ContentType.objects.get(app_label='misc', model='page')
            hit, _ = HitCount.objects.get_or_create(content_type=page, object_id=page_id)
            hit.hits = F('hits') + 1
            hit.save()
        
    return HttpResponse(json.dumps({}), content_type='application/json')

def content(request, page_url):
    try:
        page = Page.objects.get(page_url=page_url)
    except Page.DoesNotExist:
        raise Http404("Page does not exist.")
    content = page.content
    for var in page.variable.all():
        content = content.replace("{{%s}}" % var.key, var.value)
    return render(request, 'misc/misc.html', {
        'content': content,
        'page_url': page.page_url,
        'page_title': page.page_title,
        'date': int(page.date.timestamp()) if page.date else "",
        'cover_image_url': page.cover_image_url,
        'template': 'misc_pages_list',
        "version_query": STATIC_VERSION
    })

def misc_pages(request):
    pages = cache.get("misc_pages")
    if not pages:
        pages = Page.objects.all().order_by('-date')
        cache.set("misc_pages", pages, 3600 * 8)
    return render(request, 'misc/misc_pages.html', {'pages': pages, 'template': 'misc_page', "version_query": STATIC_VERSION})