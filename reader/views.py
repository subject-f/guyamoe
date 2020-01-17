from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound
from django.views.decorators.http import condition
from django.views.generic import DetailView, TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page, cache_control
from django.core.cache import cache
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import condition
from django.utils.decorators import decorator_from_middleware
from .middleware import OnlineNowMiddleware
from .models import HitCount, Series, Volume, Chapter
from datetime import datetime, timedelta, timezone
from .users_cache_lib import get_user_ip
from collections import OrderedDict, defaultdict
from api.api import all_chapter_data_etag, chapter_data_etag, md_series_page_data, md_series_data, nh_series_data
from guyamoe.settings import CANONICAL_ROOT_DOMAIN

import os
import json
import requests


@csrf_exempt
@decorator_from_middleware(OnlineNowMiddleware)
def hit_count(request):
    if request.POST:
        user_ip = get_user_ip(request)
        page_id = f"url_{request.POST['series']}/{request.POST['chapter'] if 'chapter' in request.POST else ''}{user_ip}"
        page_hits_cache = f"url_{request.POST['series']}/{request.POST['chapter'] if 'chapter' in request.POST else ''}"
        cache.set(page_id, page_id, 60)
        page_cached_users = cache.get(page_hits_cache)
        if page_cached_users:
            page_cached_users = [ip for ip in page_cached_users if cache.get(ip)]
        else:
            page_cached_users = []
        if user_ip not in page_cached_users:
            page_cached_users.append(user_ip)
            series_slug = request.POST["series"]
            series_id = Series.objects.get(slug=series_slug).id
            series = ContentType.objects.get(app_label='reader', model='series')
            hit, _ = HitCount.objects.get_or_create(content_type=series, object_id=series_id)
            hit.hits = F('hits') + 1
            hit.save()
            if "chapter" in request.POST:
                chapter_number = request.POST["chapter"]
                group_id = request.POST["group"]
                chapter = ContentType.objects.get(app_label='reader', model='chapter')
                hit, _ = HitCount.objects.get_or_create(content_type=chapter, object_id=Chapter.objects.get(chapter_number=float(chapter_number), group__id=group_id, series__id=series_id).id)
                hit.hits = F('hits') + 1
                hit.save()
        
        cache.set(page_hits_cache, page_cached_users)
    return HttpResponse(json.dumps({}), content_type='application/json')

def series_page_data(series_slug):
    series_page_dt = cache.get(f"series_page_dt_{series_slug}")
    if not series_page_dt:
        series = get_object_or_404(Series, slug=series_slug)
        chapters = Chapter.objects.filter(series=series).select_related('series', 'group')
        latest_chapter = chapters.latest('uploaded_on')
        vols = Volume.objects.filter(series=series).order_by('-volume_number')
        cover_vol_url = ""
        cover_vol_url_webp = ""
        for vol in vols:
            if vol.volume_cover:
                cover_vol_url = f"/media/{vol.volume_cover}"
                cover_vol_url_webp = cover_vol_url.rsplit(".", 1)[0] + ".webp"
                break
        content_series = ContentType.objects.get(app_label='reader', model='series')
        hit, _ = HitCount.objects.get_or_create(content_type=content_series, object_id=series.id)
        chapter_list = []
        volume_dict = defaultdict(list)
        chapter_dict = OrderedDict()
        for chapter in chapters:
            ch_clean = chapter.clean_chapter_number()
            if ch_clean in chapter_dict:
                if chapter.uploaded_on > chapter_dict[ch_clean][0].uploaded_on:
                    chapter_dict[ch_clean] = [chapter, True]
                else:
                    chapter_dict[ch_clean] = [chapter_dict[ch_clean][0], True]
            else:
                chapter_dict[ch_clean] = [chapter, False]
        for ch in chapter_dict:
            chapter, multiple_groups = chapter_dict[ch]
            u = chapter.uploaded_on
            chapter_list.append([chapter.clean_chapter_number(), chapter.title, chapter.slug_chapter_number(), chapter.group.name if not multiple_groups else "Multiple Groups", [u.year, u.month-1, u.day, u.hour, u.minute, u.second], chapter.volume])
            volume_dict[chapter.volume].append([chapter.clean_chapter_number(), chapter.slug_chapter_number(), chapter.group.name if not multiple_groups else "Multiple Groups", [u.year, u.month-1, u.day, u.hour, u.minute, u.second]])
        volume_list = []
        for key, value in volume_dict.items():
            volume_list.append([key, sorted(value, key=lambda x: float(x[0]), reverse=True)])
        chapter_list.sort(key=lambda x: float(x[0]), reverse=True)
        series_page_dt = {
                "series": series.name,
                "alt_titles": series.alternative_titles.split(", ") if series.alternative_titles else [],
                "alt_titles_str": f" Alternative titles: {series.alternative_titles}." if series.alternative_titles else "",
                "series_id": series.id,
                "slug": series.slug,
                "cover_vol_url": cover_vol_url,
                "cover_vol_url_webp": cover_vol_url_webp,
                "views": hit.hits + 1,
                "synopsis": series.synopsis, 
                "author": series.author.name,
                "artist": series.artist.name,
                "last_added": [latest_chapter.clean_chapter_number(), latest_chapter.uploaded_on.timestamp() * 1000],
                "chapter_list": chapter_list,
                "volume_list": sorted(volume_list, key=lambda m: m[0], reverse=True),
                "root_domain": CANONICAL_ROOT_DOMAIN,
                "relative_url":f"read/manga/{series.slug}/"
        }
        cache.set(f"series_page_dt_{series_slug}", series_page_dt, 3600 * 12)
    return series_page_dt

@cache_control(max_age=60)
@condition(etag_func=chapter_data_etag)
@decorator_from_middleware(OnlineNowMiddleware)
def series_info(request, series_slug):
    data = series_page_data(series_slug)
    return render(request, 'reader/series_info.html', data)

@staff_member_required
@decorator_from_middleware(OnlineNowMiddleware)
def series_info_admin(request, series_slug):
    data = series_page_data(series_slug)
    return render(request, 'reader/series_info_admin.html', data)

def get_all_metadata(series_slug):
    series_metadata = cache.get(f"series_metadata_{series_slug}")
    if not series_metadata:
        series = Series.objects.get(slug=series_slug)
        chapters = Chapter.objects.filter(series=series).select_related('series')
        series_metadata = {}
        for chapter in chapters:
            series_metadata[chapter.slug_chapter_number()] = {"series_name": chapter.series.name, "slug": chapter.series.slug, "chapter_number": chapter.clean_chapter_number(), "chapter_title": chapter.title, "version_query": settings.STATIC_VERSION}
        cache.set(f"series_metadata_{series_slug}", series_metadata, 3600 * 12)
    return series_metadata

@cache_control(max_age=120)
@decorator_from_middleware(OnlineNowMiddleware)
def reader(request, series_slug, chapter, page):
    metadata = get_all_metadata(series_slug)
    if chapter in metadata:
        metadata[chapter]["relative_url"] = f"read/manga/{series_slug}/{chapter}/1"
        return render(request, 'reader/reader.html', metadata[chapter])
    else:
        return render(request, 'homepage/how_cute_404.html', status=404)

@decorator_from_middleware(OnlineNowMiddleware)
def md_proxy(request, md_series_id):
    metadata = md_series_page_data(md_series_id)
    if metadata:
        metadata["relative_url"] = f"md_proxy/{md_series_id}"
        return render(request, 'reader/md_series.html', metadata)
    else:
        return render(request, 'reader/md_down.html', metadata)

@decorator_from_middleware(OnlineNowMiddleware)
def md_chapter(request, md_series_id, chapter, page):
    data = md_series_data(md_series_id)
    if data and chapter.replace("-", ".") in data["chapters"]:
        data["relative_url"] = f"md_proxy/{md_series_id}/{chapter}/{page}"
        return render(request, 'reader/reader.html', data)
    else:
        return render(request, 'homepage/how_cute_404.html', status=404)

def nh_proxy(request, nh_series_id):
    metadata = nh_series_data(nh_series_id)
    if metadata:
        metadata["relative_url"] = f"nh_proxy/{nh_series_id}"
        return render(request, 'reader/nh_series.html', metadata)
    else:
        return render(request, 'reader/how_cute_404.html', status=404)

def nh_chapter(request, nh_series_id, chapter, page):
    data = nh_series_data(nh_series_id)
    if data and chapter.replace("-", ".") in data["chapters"]:
        data["relative_url"] = f"nh_proxy/{nh_series_id}/{chapter}/{page}"
        return render(request, 'reader/reader.html', data)
    else:
        return render(request, 'homepage/how_cute_404.html', status=404)