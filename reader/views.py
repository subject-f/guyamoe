from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound
from django.views.generic import DetailView, TemplateView
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from .models import HitCount, Series, Volume, Chapter
from datetime import datetime, timedelta, timezone
from .users_cache_lib import curr_user_and_online
from collections import defaultdict
import os
import json


def hit_count(request):
    if request.POST:
        ### Install and test with memcache first
        user_ip = curr_user_and_online(request)
        page_id = f"url_{request.POST['series']}/{request.POST['chapter'] if 'chapter' in request.POST else ''}{user_ip}"
        page_hits_cache = f"url_{request.POST['series']}/{request.POST['chapter'] if 'chapter' in request.POST else ''}"
        cache.set(page_id, page_id, 600)

        page_cached_users = cache.get(page_hits_cache)
        print("page_cached_users", page_cached_users)
        if page_cached_users:
            page_cached_users = [ip for ip in page_cached_users if cache.get(ip)]
        else:
            page_cached_users = []
        if user_ip not in page_cached_users:
            page_cached_users.append(user_ip)
            series_id = request.POST["series"]
            series = ContentType.objects.get(app_label='reader', model='series')
            hit, _ = HitCount.objects.get_or_create(content_type=series, object_id=series_id)
            hit.hits = F('hits') + 1
            hit.save()
            if "chapter" in request.POST:
                chapter_id = request.POST["chapter"]
                chapter = ContentType.objects.get(app_label='reader', model='chapter')
                hit, _ = HitCount.objects.get_or_create(content_type=chapter, object_id=chapter_id)
                hit.hits = F('hits') + 1
                hit.save()
        
        print("page_cached_users new", page_cached_users)
        cache.set(page_hits_cache, page_cached_users)
        print(page_hits_cache)
        page_cached_users = cache.get(page_hits_cache)
        print("page_hits_cache new 2", page_cached_users)

        
        return HttpResponse(json.dumps({}), content_type='application/json')


@cache_page(1)
def series_info(request, series_slug):
    series = get_object_or_404(Series, slug=series_slug)
    chapters = Chapter.objects.filter(series=series)
    latest_chapter = chapters.latest('id')
    vols = Volume.objects.filter(series=series).order_by('-volume_number')
    cover_vol_url = ""
    for vol in vols:
        if vol.volume_cover:
            cover_vol_url = f"/media/{vol.volume_cover}"
            break
    content_series = ContentType.objects.get(app_label='reader', model='series')
    hit, _ = HitCount.objects.get_or_create(content_type=content_series, object_id=series.id)
    chapter_list = []
    volume_dict = defaultdict(list)
    for chapter in chapters:
        upload_date = chapter.get_chapter_time()
        chapter_list.append([chapter.clean_chapter_number(), chapter.title, chapter.slug_chapter_number(), chapter.group.name, upload_date, chapter.volume])
        volume_dict[chapter.volume].append([chapter.clean_chapter_number(), chapter.slug_chapter_number(), chapter.group.name, upload_date])
    volume_list = []
    for key, value in volume_dict.items():
        volume_list.append([key, sorted(value, key=lambda x: float(x[0]), reverse=True)])
    chapter_list.sort(key=lambda x: float(x[0]), reverse=True)
    return render(request, 'reader/series_info.html', {
            "series": series.name,
            "series_id": series.id,
            "slug": series.slug,
            "cover_vol_url": cover_vol_url,
            "views": hit.hits + 1,
            "synopsis": series.synopsis, 
            "author": series.author.name,
            "artist": series.artist.name,
            "last_added": [latest_chapter.clean_chapter_number(), latest_chapter.get_chapter_time()],
            "chapter_list": chapter_list,
            "volume_list": sorted(volume_list, key=lambda m: m[0], reverse=True),
            "is_mod": request.user.is_staff
        })


@cache_page(1)
def reader(request, series_slug, chapter, page):
    slug_chapter_numb = chapter.replace("-", ".")
    chapter = get_object_or_404(Chapter, series__slug=series_slug, chapter_number=slug_chapter_numb)
    return render(request, 'reader/reader.html', {
        "series_id": chapter.series.id,
        "chapter_id": chapter.id
    })
