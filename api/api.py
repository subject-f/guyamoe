from ast import literal_eval
import random
import os
import json
import zipfile
import re
import base64
from datetime import datetime
from io import BytesIO;
from PIL import ImageFilter, Image
from django.conf import settings
from django.core.cache import cache
from reader.models import Series, Volume, Chapter, Group

def all_chapter_data_etag(request):
    etag = cache.get("all_chapter_data_etag")
    if not etag:
        etag = str(datetime.now())
        cache.set(f"all_chapter_data_etag", etag, 48 * 3600)
    return etag

def chapter_data_etag(request, series_slug):
    etag = cache.get(f"{series_slug}_chapter_data_etag")
    if not etag:
        etag = str(datetime.now())
        cache.set(f"{series_slug}_chapter_data_etag", etag, 48 * 3600)
    return etag

def series_data(series_slug):
    series = Series.objects.get(slug=series_slug)
    chapters = Chapter.objects.filter(series=series).select_related('group')
    chapters_dict = {}
    groups_dict = {}
    for chapter in chapters:
        chapter_media_path = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", chapter.folder)
        ch_clean = Chapter.clean_chapter_number(chapter)
        groups_dict[str(chapter.group.id)] = chapter.group.name
        query_string = "" if not chapter.version else f"?v{chapter.version}"
        if ch_clean in chapters_dict:
            chapters_dict[ch_clean]["groups"][str(chapter.group.id)] = sorted([u + query_string for u in os.listdir(os.path.join(chapter_media_path, str(chapter.group.id)))])
            chapters_dict[ch_clean]["release_date"][str(chapter.group.id)] = int(chapter.uploaded_on.timestamp())
        else:
            chapters_dict[ch_clean] = {
                "volume": str(chapter.volume),
                "title": chapter.title,
                "folder": chapter.folder,
                "groups": {
                    str(chapter.group.id): sorted([u + query_string for u in os.listdir(os.path.join(chapter_media_path, str(chapter.group.id)))])
                },
                "release_date": {
                    str(chapter.group.id): int(chapter.uploaded_on.timestamp())
                }
            }
            if chapter.wo and chapter.wo != 0:
                chapters_dict[ch_clean]["wo"] = chapter.wo
        if chapter.preferred_sort:
            try:
                chapters_dict[ch_clean]["preferred_sort"] = literal_eval(chapter.preferred_sort)
            except:
                pass
    vols = Volume.objects.filter(series=series).order_by('-volume_number')
    cover_vol_url = ""
    for vol in vols:
        if vol.volume_cover:
            cover_vol_url = f"/media/{vol.volume_cover}"
            break
    return {"slug": series_slug, "title": series.name, "description": series.synopsis, "author": series.author.name, "artist": series.artist.name, "groups": groups_dict, "cover": cover_vol_url, "preferred_sort": settings.PREFERRED_SORT, "chapters": chapters_dict}

def series_data_cache(series_slug):
    series_api_data = series_data(series_slug)
    cache.set(f"series_api_data_{series_slug}", series_api_data, 3600 * 48)
    return series_api_data

def all_groups():
    groups_data = cache.get(f"all_groups_data")
    if not groups_data:
        groups_data = {str(group.id) : group.name for group in Group.objects.all()}
        cache.set(f"all_groups_data", groups_data, 3600 * 12)
    return groups_data

def random_chars():
    return ''.join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=8))

def create_preview_pages(chapter_folder, group_folder, page_file):
    shrunk = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    page_name, ext = page_file.rsplit(".", 1)
    if shrunk.width > shrunk.height:
        if "_w." not in page_file:
            page_file = page_name + "_w." + ext
            shrunk.save(os.path.join(chapter_folder, group_folder, page_file))
            os.remove(os.path.join(chapter_folder, group_folder, page_name + "." + ext))
            shrunk = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    else:
        if "_w." in page_file:
            page_file = page_file.replace("_w", "")
            shrunk.save(os.path.join(chapter_folder, group_folder, page_file))
            os.remove(os.path.join(chapter_folder, group_folder, page_name + "." + ext))
            shrunk = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    blur = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    shrunk = shrunk.convert("RGB")
    blur = blur.convert("RGB")
    shrunk.thumbnail((shrunk.width, 250), Image.ANTIALIAS)
    blur.thumbnail((blur.width/8, blur.height/8), Image.ANTIALIAS)
    shrunk.save(os.path.join(chapter_folder, f"{group_folder}_shrunk", page_file), "JPEG", quality=100, optimize=True, progressive=True)
    blur = blur.filter(ImageFilter.GaussianBlur(radius=2))
    blur.save(os.path.join(chapter_folder, f"{group_folder}_shrunk_blur", page_file), "JPEG", quality=100, optimize=True, progressive=True)

def index_chapter(chapter):
    if hasattr(settings, "OCR_SCRIPT_PATH") and os.path.exists(settings.OCR_SCRIPT_PATH):
        ch_slug = chapter.slug_chapter_number()
        group_folder = str(chapter.group.id)
        curr_chap_index_priority = settings.PREFERRED_SORT.index(str(chapter.group.id))
        all_chap_versions = [ch.group.id for ch in Chapter.objects.filter(chapter_number=chapter.chapter_number, series=chapter.series)]
        for version in all_chap_versions:
            try:
                if settings.PREFERRED_SORT.index(str(version)) <= curr_chap_index_priority:
                    break
            except ValueError:
                continue
        else:
            return
        print("Deleting old chapter index from db.")
        for index in ChapterIndex.objects.filter(series=chapter.series):
            if ch_slug in index.chapter_and_pages:
                print(index.word, index.chapter_and_pages[ch_slug])
                del index.chapter_and_pages[ch_slug]
                index.save()
        print("Finished deleting old chapter index from db.")
        print("Indexing chapter pages...")
        chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", chapter.series.slug, "chapters", chapter.folder)
        subprocess.Popen(f'bash {settings.OCR_SCRIPT_PATH} {chapter_folder}/{group_folder} {chapter.clean_chapter_number()} {chapter.clean_chapter_number()}_{chapter.series.id} {chapter.series.slug}'.split())

def chapter_post_process(chapter, update_version=True):
    print(chapter.series, chapter.chapter_number)
    chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", chapter.series.slug, "chapters", chapter.folder)
    group = str(chapter.group.id)
    shrunk = os.path.join(chapter_folder, f"{group}_shrunk")
    blur = os.path.join(chapter_folder, f"{group}_shrunk_blur")
    os.makedirs(shrunk, exist_ok=True)
    os.makedirs(blur, exist_ok=True)
    [os.remove(os.path.join(chapter_folder, shrunk, f)) for f in os.listdir(shrunk)]
    [os.remove(os.path.join(chapter_folder, blur, f)) for f in os.listdir(blur)]
    all_pages = os.listdir(os.path.join(chapter_folder, group))
    for idx, page in enumerate(all_pages):
        create_preview_pages(chapter_folder, group, page)
    zip_chapter(chapter.series.slug, chapter.chapter_number, chapter.group)
    if update_version:
        chapter.version = chapter.version + 1 if chapter.version else 2
        chapter.save()
    clear_pages_cache()
    index_chapter(chapter)

def clear_series_cache(series_slug):
    cache.delete(f"series_api_data_{series_slug}")
    cache.delete(f"series_page_data_{series_slug}")
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

def zip_volume(series_slug, volume):
    zip_filename = f"{series_slug}_vol_{volume}.zip"
    zip_file = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename)
    zf = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename), "w")
    checked_chapters = set([])
    for chapter in Chapter.objects.filter(series__slug=series_slug, volume=volume):
        if chapter.chapter_number in checked_chapters:
            continue
        checked_chapters.add(chapter.chapter_number)
        chapter_media_path = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", chapter.folder)
        groups = os.listdir(chapter_media_path)
        for group in settings.PREFERRED_SORT:
            if group in groups:
                ch_obj = Chapter.objects.filter(series__slug=series_slug, folder=chapter.folder, group__id=group).first()
                if not ch_obj:
                    continue
                group_dir = os.path.join(chapter_media_path, group)
                for root, _, files in os.walk(group_dir):
                    for f in files:
                        zf.write(os.path.join(root, f), os.path.join(ch_obj.clean_chapter_number(), f))
                break
        else:
            continue
    zf.close()
    with open(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename), "rb") as fh:
        zip_file = fh.read()
    return zip_file, zip_filename

def zip_chapter(series_slug, chapter, group):
    ch_obj = Chapter.objects.filter(series__slug=series_slug, chapter_number=chapter, group=group).first()
    chapter_dir = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", ch_obj.folder)
    chapter_pages = [os.path.join(chapter_dir, str(group.id), f) for f in os.listdir(os.path.join(chapter_dir, str(group.id)))]
    zip_filename = f"{ch_obj.group.id}_{ch_obj.slug_chapter_number()}.zip"
    zf = zipfile.ZipFile(os.path.join(chapter_dir, zip_filename), "w")
    for fpath in chapter_pages:
        _, fname = os.path.split(fpath)
        zf.write(fpath, fname)
    zf.close()
    with open(os.path.join(chapter_dir, zip_filename), "rb") as fh:
        zip_file = fh.read()
    return zip_file, zip_filename, fname
