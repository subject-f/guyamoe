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
from bs4 import BeautifulSoup
import requests
import re
from api.api import all_chapter_data_etag, chapter_data_etag, md_series_data, get_md_data, nh_series_data, fs_decode_url, fs_series_data, ENCODE_STR_SLASH
from guyamoe.settings import CANONICAL_ROOT_DOMAIN, STATIC_VERSION

import os
import json
import requests


@csrf_exempt
@decorator_from_middleware(OnlineNowMiddleware)
def hit_count(request):
    if request.method == "POST":
        user_ip = get_user_ip(request)
        page_id = f"url_{request.POST['series']}/{request.POST['chapter'] if 'chapter' in request.POST else ''}{user_ip}"
        if not cache.get(page_id):
            cache.set(page_id, page_id, 60)
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
            chapter_list.append([chapter.clean_chapter_number(), chapter.clean_chapter_number(), chapter.title, chapter.slug_chapter_number(), chapter.group.name if not multiple_groups else "Multiple Groups", [u.year, u.month-1, u.day, u.hour, u.minute, u.second], chapter.volume])
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
                "metadata": [
                    ["Author", series.author.name], 
                    ["Artist", series.artist.name], 
                    ["Views", hit.hits + 1],
                    ["Last Updated", f"Ch. {latest_chapter.clean_chapter_number()} - {datetime.utcfromtimestamp(latest_chapter.uploaded_on.timestamp()).strftime('%Y-%m-%d')}"]
                ],
                "synopsis": series.synopsis, 
                "author": series.author.name,
                "chapter_list": chapter_list,
                "volume_list": sorted(volume_list, key=lambda m: m[0], reverse=True),
                "root_domain": CANONICAL_ROOT_DOMAIN,
                "relative_url":f"read/manga/{series.slug}/",
                "available_features": ["detailed", "compact", "volumeCovers", "rss", "download"],
                "reader_modifier": "manga"
        }
        cache.set(f"series_page_dt_{series_slug}", series_page_dt, 3600 * 12)
    return series_page_dt

def md_series_page_data(series_id):
    md_series_page_dt = cache.get(f"md_series_page_dt_{series_id}")
    if not md_series_page_dt:
        resp = get_md_data(f"https://mangadex.org/api/?id={series_id}&type=manga")
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            chapter_list = []
            latest_chap_id = next(iter(api_data["chapter"]))
            date = datetime.utcfromtimestamp(api_data["chapter"][latest_chap_id]["timestamp"])
            last_updated = (api_data["chapter"][latest_chap_id]["chapter"], datetime.utcfromtimestamp(api_data["chapter"][latest_chap_id]["timestamp"]).strftime('%Y-%m-%d'))
            chapter_dict = {}
            for ch in api_data["chapter"]:
                if api_data["chapter"][ch]["lang_code"] == "gb":
                    chapter_id = api_data["chapter"][ch]["chapter"]
                    chapter_list_id = api_data["chapter"][ch]["chapter"]
                    try:
                        float(api_data["chapter"][ch]["chapter"])
                    except ValueError:
                        chapter_id = f"0.0{str(api_data['chapter'][ch]['timestamp'])}"
                        chapter_list_id = ""
                    date = datetime.utcfromtimestamp(api_data["chapter"][ch]["timestamp"])
                    if api_data["chapter"][ch]["chapter"] in chapter_dict:
                        chapter_dict[chapter_id] = [chapter_list_id, chapter_id, api_data["chapter"][ch]["title"], chapter_id.replace(".", "-"), "Multiple Groups", [date.year, date.month-1, date.day, date.hour, date.minute, date.second], api_data["chapter"][ch]["volume"]]
                    else:
                        chapter_dict[chapter_id] = [chapter_list_id, chapter_id, api_data["chapter"][ch]["title"], chapter_id.replace(".", "-"), api_data["chapter"][ch]["group_name"], [date.year, date.month-1, date.day, date.hour, date.minute, date.second], api_data["chapter"][ch]["volume"]]
            chapter_list = [x[1] for x in sorted(chapter_dict.items(), key=lambda m: float(m[0]), reverse=True)]
            md_series_page_dt = {
                "series": api_data["manga"]["title"],
                "alt_titles": [],
                "alt_titles_str": None,
                "slug": series_id,
                "cover_vol_url": "https://mangadex.org" + api_data["manga"]["cover_url"],
                "metadata": [
                    ["Author", api_data["manga"]["author"]], 
                    ["Artist", api_data["manga"]["artist"]],
                    ["Last Updated", f"Ch. {last_updated[0]} - {last_updated[1]}"]
                ],
                "synopsis": api_data["manga"]["description"], 
                "author": api_data["manga"]["author"],
                "chapter_list": chapter_list,
                "root_domain": CANONICAL_ROOT_DOMAIN,
                "relative_url": f"read/md_proxy/{series_id}",
                "original_url": f"https://mangadex.org/title/{series_id}",
                "available_features": ["detailed"],
                "reader_modifier": "md_proxy"
            }
            cache.set(f"md_series_page_dt_{series_id}", md_series_page_dt, 60 * 5)
        else:
            return None
    return md_series_page_dt

def fs_series_page_data(encoded_url):
    fs_series_page_dt = cache.get(f"fs_series_page_dt_{encoded_url}")
    if not fs_series_page_dt:
        try:
            resp = requests.post(f"https://{fs_decode_url(encoded_url)}/", data={"adult":"true"})
        except requests.exceptions.ConnectionError:
            resp = requests.post(f"http://{fs_decode_url(encoded_url)}/", data={"adult":"true"})
        if resp.status_code == 200:
            data = resp.text
            soup = BeautifulSoup(data, "html.parser")

            comic_info = soup.find("div", class_="large comic")

            title = comic_info.find("h1", class_="title").get_text().replace("\n", "").strip()
            description = comic_info.find("div", class_="info").get_text().strip()
            groups_dict = {"1": encoded_url.split(ENCODE_STR_SLASH)[0]}
            cover_div = soup.find("div", class_="thumbnail")
            if cover_div and cover_div.find("img")["src"]:
                cover = cover_div.find("img")["src"]
            else:
                cover = ""

            chapter_list = []

            for a in soup.find_all("div", class_="element"):
                link = a.find("div", class_="title").find("a")
                chapter_regex = re.search(r'(Chapter |Ch.)([\d.]+)', link.get_text())
                chapter_number = "0"
                if chapter_regex:
                    chapter_number = chapter_regex.group(2)
                volume_regex = re.search(r'(Volume |Vol.)([\d.]+)', link.get_text())
                volume_number = "1"
                if volume_regex:
                    volume_number = volume_regex.group(2)
                chapter_title = link.get_text()
                upload_info = list(map(lambda e: e.strip(), a.find("div", class_="meta_r").get_text().replace("by", "").split(",")))
                chapter_list.append([chapter_number, chapter_number, chapter_title, chapter_number.replace(".", "-"), upload_info[0], upload_info[1], ""])

            fs_series_page_dt = {
                "series": title,
                "alt_titles": [],
                "alt_titles_str": None,
                "slug": encoded_url,
                "cover_vol_url": cover,
                "metadata": [],
                "synopsis": description,
                "author": "FoolSlide",
                "chapter_list": chapter_list,
                "root_domain": CANONICAL_ROOT_DOMAIN,
                "relative_url": f"read/fs_proxy/{encoded_url}",
                "original_url": f"https://{fs_decode_url(encoded_url)}",
                "available_features": ["detailed"],
                "reader_modifier": "fs_proxy"
            }
            cache.set(f"fs_series_page_dt_{encoded_url}", fs_series_page_dt, 60 * 5)
        else:
            return None
    return fs_series_page_dt

def nh_series_page_data(series_id):
    nh_series_page_dt = cache.get(f"nh_series_page_dt_{series_id}")
    if not nh_series_page_dt:
        data = nh_series_data(series_id)
        if data:
            date = datetime.utcfromtimestamp(data["timestamp"])
            chapter_list = [
                ["", "1", data["title"], "1", data["group"] or "NHentai", [date.year, date.month-1, date.day, date.hour, date.minute, date.second], ""]
            ]
            nh_series_page_dt = {
                "series": data["title"],
                "alt_titles": [],
                "alt_titles_str": None,
                "slug": data["slug"],
                "cover_vol_url": data["cover"],
                "metadata": [
                    ["Author", data["artist"]],
                    ["Language", data["lang"]]
                ],
                "synopsis": f"{data['description']}\n\n{' - '.join(data['tags'])}",
                "author": data["artist"],
                "chapter_list": chapter_list,
                "root_domain": CANONICAL_ROOT_DOMAIN,
                "relative_url": f"read/nh_proxy/{series_id}",
                "original_url": f"https://nhentai.net/g/{series_id}",
                "available_features": ["detailed"],
                "reader_modifier": "nh_proxy"
            }
            cache.set(f"nh_series_page_dt_{series_id}", nh_series_page_dt, 3600 * 24)
        else:
            return None
    return nh_series_page_dt

@cache_control(max_age=60)
@condition(etag_func=chapter_data_etag)
@decorator_from_middleware(OnlineNowMiddleware)
def series_info(request, series_slug):
    data = series_page_data(series_slug)
    data["version_query"] = STATIC_VERSION
    return render(request, 'reader/series.html', data)

@staff_member_required
@decorator_from_middleware(OnlineNowMiddleware)
def series_info_admin(request, series_slug):
    data = series_page_data(series_slug)
    data["version_query"] = STATIC_VERSION
    data["available_features"].append("admin")
    return render(request, 'reader/series.html', data)

def get_all_metadata(series_slug):
    series_metadata = cache.get(f"series_metadata_{series_slug}")
    if not series_metadata:
        series = Series.objects.get(slug=series_slug)
        chapters = Chapter.objects.filter(series=series).select_related('series')
        series_metadata = {}
        for chapter in chapters:
            series_metadata[chapter.slug_chapter_number()] = {"series_name": chapter.series.name, "slug": chapter.series.slug, "chapter_number": chapter.clean_chapter_number(), "chapter_title": chapter.title}
        cache.set(f"series_metadata_{series_slug}", series_metadata, 3600 * 12)
    return series_metadata

@cache_control(max_age=120)
@decorator_from_middleware(OnlineNowMiddleware)
def reader(request, series_slug, chapter, page=None):
    if page:
        data = get_all_metadata(series_slug)
        if chapter in data:
            data[chapter]["relative_url"] = f"read/manga/{series_slug}/{chapter}/1"
            data[chapter]["version_query"] = STATIC_VERSION
            data[chapter]["first_party"] = True
            return render(request, 'reader/reader.html', data[chapter])
        else:
            return render(request, 'homepage/how_cute_404.html', status=404)
    else:
        return redirect('reader-manga-chapter', series_slug, chapter, "1")

@decorator_from_middleware(OnlineNowMiddleware)
def md_proxy(request, md_series_id):
    data = md_series_page_data(md_series_id)
    if data:
        data["version_query"] = STATIC_VERSION
        data["hide_referrer"] = True
        return render(request, 'reader/series.html', data)
    else:
        return HttpResponse(status=500)

@decorator_from_middleware(OnlineNowMiddleware)
def md_chapter(request, md_series_id, chapter, page):
    data = md_series_data(md_series_id)
    if data and chapter.replace("-", ".") in data["chapters"]:
        data["relative_url"] = f"read/md_proxy/{md_series_id}/{chapter}/{page}"
        data["hide_referrer"] = True
        data["version_query"] = STATIC_VERSION
        data["series_name"] = data["title"]
        return render(request, 'reader/reader.html', data)
    else:
        return HttpResponse(status=500)

@decorator_from_middleware(OnlineNowMiddleware)
def nh_proxy(request, nh_series_id):
    data = nh_series_page_data(nh_series_id)
    if data:
        data["version_query"] = STATIC_VERSION
        data["hide_referrer"] = True
        return render(request, 'reader/series.html', data)
    else:
        return HttpResponse(status=500)

@decorator_from_middleware(OnlineNowMiddleware)
def nh_chapter(request, nh_series_id, chapter, page):
    data = nh_series_data(nh_series_id)
    if data and chapter.replace("-", ".") in data["chapters"]:
        data["relative_url"] = f"read/nh_proxy/{nh_series_id}/{chapter}/{page}"
        data["hide_referrer"] = True
        data["version_query"] = STATIC_VERSION
        data["series_name"] = data["title"]
        return render(request, 'reader/reader.html', data)
    else:
        return HttpResponse(status=500)

@decorator_from_middleware(OnlineNowMiddleware)
def fs_proxy(request, encoded_url):
    data = fs_series_page_data(encoded_url)
    if data:
        data["version_query"] = STATIC_VERSION
        data["hide_referrer"] = True
        return render(request, 'reader/series.html', data)
    else:
        return HttpResponse(status=500)

@decorator_from_middleware(OnlineNowMiddleware)
def fs_chapter(request, encoded_url, chapter, page):
    data = fs_series_data(encoded_url)
    if data and chapter.replace("-", ".") in data["chapters"]:
        data["relative_url"] = f"read/fs_proxy/{encoded_url}/{chapter}/{page}"
        data["hide_referrer"] = True
        data["version_query"] = STATIC_VERSION
        data["series_name"] = data["title"]
        return render(request, 'reader/reader.html', data)
    else:
        return HttpResponse(status=500)
