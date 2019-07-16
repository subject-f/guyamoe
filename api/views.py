from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.db import IntegrityError
from ratelimit.decorators import ratelimit
from django.core.cache import cache
from datetime import datetime, timezone
from reader.models import Series, Volume, Chapter, Group
from PIL import ImageFilter, Image
import random
import os
import json
import zipfile


@ratelimit(key='ip', rate='10/20s', block=True)
def series_data(request, series_slug):
    series_api_data = cache.get(f"series_api_data_{series_slug}")
    if not series_api_data:
        series = Series.objects.get(slug=series_slug)
        chapters = Chapter.objects.filter(series=series).select_related('group')
        chapters_dict = {}
        for chapter in chapters:
            chapter_media_path = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", chapter.folder)
            ch_clean = Chapter.clean_chapter_number(chapter)
            if ch_clean in chapters_dict:
                chapters_dict[ch_clean]["groups"][str(chapter.group.id)] = sorted(os.listdir(os.path.join(chapter_media_path, str(chapter.group.id))))
            else:
                chapters_dict[ch_clean] = {
                    "volume": str(chapter.volume),
                    "title": chapter.title,
                    "folder": chapter.folder,
                    "groups": {
                        str(chapter.group.id): sorted(os.listdir(os.path.join(chapter_media_path, str(chapter.group.id))))
                    }
                }
        series_api_data = {"slug": series_slug, "title": series.name, "chapters": chapters_dict}
        cache.set(f"series_api_data_{series_slug}", series_api_data, 3600 * 12)
    return HttpResponse(JsonResponse(series_api_data))

@ratelimit(key='ip', rate='5/10s')
def get_groups(request, series_slug):
    groups_data = cache.get(f"groups_data_{series_slug}")
    if not groups_data:
        groups_data = {str(ch.group.id) : ch.group.name for ch in Chapter.objects.filter(series__slug=series_slug)}
        cache.set(f"groups_data_{series_slug}", groups_data, 3600 * 12)
    return HttpResponse(JsonResponse({"groups": groups_data}))


def random_chars():
    return ''.join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=8))

def create_preview_pages(chapter_folder, group_folder, page_file):
    shrunk = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    blur = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    shrunk = shrunk.convert("RGB")
    blur = blur.convert("RGB")
    shrunk.thumbnail((shrunk.width, 250), Image.ANTIALIAS)
    blur.thumbnail((blur.width/8, blur.height/8), Image.ANTIALIAS)
    shrunk.save(os.path.join(chapter_folder, f"{group_folder}_shrunk", page_file), "JPEG", quality=100, optimize=True, progressive=True)
    blur = blur.filter(ImageFilter.GaussianBlur(radius=2))
    blur.save(os.path.join(chapter_folder, f"{group_folder}_shrunk_blur", page_file), "JPEG", quality=100, optimize=True, progressive=True)

def upload_new_chapter(request, series_slug):
    if request.POST and request.user and request.user.is_staff:
        group = Group.objects.get(name=request.POST["scanGroup"])
        series = Series.objects.get(slug=series_slug)
        chapter_number = float(request.POST["chapterNumber"])
        existing_chapter = Chapter.objects.filter(chapter_number=chapter_number, series=series).first()
        chapter_folder_numb = f"{int(chapter_number):04}"
        chapter_folder_numb += f"-{str(chapter_number).rsplit('.')[1]}_" if not str(chapter_number).endswith("0") else "_"
        if not existing_chapter:
            uid = chapter_folder_numb + random_chars()
        else:
            if Chapter.objects.filter(chapter_number=chapter_number, series=series, group=group).first():
                return HttpResponse(JsonResponse({"response": "Error: This chapter by this group already exists! Click on edit next to the existing chapter for overwriting."}))
            else:
                uid = existing_chapter.folder
        Chapter.objects.create(chapter_number=chapter_number, group=group, series=series, folder=uid, title=request.POST["chapterTitle"], volume=request.POST["volumeNumber"], uploaded_on=datetime.utcnow().replace(tzinfo=timezone.utc))
        chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", uid)
        group_folder = str(group.id)
        if os.path.exists(os.path.join(chapter_folder, group_folder)):
            return HttpResponse(JsonResponse({"response": "Error: This chapter by this group already exists but wasn't recorded in the database. Chapter has been recorded but not uploaded."}))
        os.makedirs(os.path.join(chapter_folder, group_folder))
        with zipfile.ZipFile(request.FILES["chapterPages"]) as zip_file:
            all_pages = sorted(zip_file.namelist())
            padding = len(str(len(all_pages)))
            for idx, page in enumerate(all_pages):
                extension = page.rsplit(".", 1)[1]
                page_file = f"{str(idx+1).zfill(padding)}.{extension}"
                with open(os.path.join(chapter_folder, group_folder, page_file), "wb") as f:
                    f.write(zip_file.read(page))
                create_preview_pages(chapter_folder, group_folder, page_file)
        return HttpResponse(json.dumps({"response": "success"}), content_type="application/json")

@ratelimit(key='ip', rate='5/10s')
def get_volume_covers(request, series_slug):
    if request.POST:
        covers = cache.get(f"vol_covers_{series_slug}")
        if not covers:
            series = Series.objects.get(slug=series_slug)
            volume_covers = Volume.objects.filter(series=series).order_by('volume_number').values_list('volume_number', 'volume_cover')
            covers = {"covers": [[cover[0], f"/media/{cover[1]}"] for cover in volume_covers]}
            cache.set(f"vol_covers_{series_slug}", covers)
        return HttpResponse(json.dumps(covers), content_type="application/json")

def clear_series_cache(series_slug):
    cache.delete(f"series_api_data_{series_slug}")
    cache.delete(f"groups_data_{series_slug}")
    cache.delete(f"vol_covers_{series_slug}")

def clear_pages_cache():
    online = cache.get("online_now")
    if not online:
        online = []
    peak_traffic = cache.get("peak_traffic")
    ip_list = []
    for ip in online:
        if cache.get(ip):
            ip_list.append(ip)
    cache.clear()
    for ip in ip_list:
        cache.set(ip, ip, 450)
    cache.set("online_now", set(ip_list), 600)
    cache.set("peak_traffic", peak_traffic, 3600 * 6)

def clear_cache(request):
    if request.POST and request.user and request.user.is_staff:
        print(request.POST["clear_type"])
        if request.POST["clear_type"] == "all":
            clear_pages_cache()
            response = "Cleared all cache"
        elif request.POST["clear_type"] == "chapter":
            for series_slug in Series.objects.all().values_list('slug'):
                clear_series_cache(series_slug)
            response = "Cleared series cache"
        else:
            response = "Not a valid option"
        return HttpResponse(json.dumps({"response": response}), content_type="application/json")
