import random
import hashlib
import os
import json
import zipfile
from io import BytesIO;
from PIL import ImageFilter, Image
from django.conf import settings
from django.core.cache import cache
from reader.models import Series, Volume, Chapter, Group

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
        else:
            chapters_dict[ch_clean] = {
                "volume": str(chapter.volume),
                "title": chapter.title,
                "folder": chapter.folder,
                "groups": {
                    str(chapter.group.id): sorted([u + query_string for u in os.listdir(os.path.join(chapter_media_path, str(chapter.group.id)))])
                }
            }
            if chapter.preferred_sort:
                try:
                    chapters_dict[ch_clean]["preferred_sort"] = json.loads(chapter.preferred_sort)
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
    series_api_hash = int(hashlib.sha256(json.dumps(series_api_data).encode('utf-8')).hexdigest(), 16) % 10**16
    cache.set(f"series_api_data_{series_slug}", series_api_data, 3600 * 48)
    cache.set(f"series_api_hash_{series_slug}", series_api_hash, 3600 * 48)
    return series_api_data, series_api_hash

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
    blur = Image.open(os.path.join(chapter_folder, group_folder, page_file))
    shrunk = shrunk.convert("RGB")
    blur = blur.convert("RGB")
    shrunk.thumbnail((shrunk.width, 250), Image.ANTIALIAS)
    blur.thumbnail((blur.width/8, blur.height/8), Image.ANTIALIAS)
    shrunk.save(os.path.join(chapter_folder, f"{group_folder}_shrunk", page_file), "JPEG", quality=100, optimize=True, progressive=True)
    blur = blur.filter(ImageFilter.GaussianBlur(radius=2))
    blur.save(os.path.join(chapter_folder, f"{group_folder}_shrunk_blur", page_file), "JPEG", quality=100, optimize=True, progressive=True)

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

def zip_series(series_slug):
    zip_filename = f"{series_slug}.zip"
    zip_file = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename)
    zf = zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename), "w")
    for chapter_folder in os.listdir(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters")):
        chapter_media_path = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", chapter_folder)
        groups = os.listdir(chapter_media_path)
        for group in settings.PREFERRED_SORT:
            if group in groups:
                ch_obj = Chapter.objects.get(series__slug=series_slug, folder=chapter_folder, group__id=group)
                group_dir = os.path.join(chapter_media_path, group)
                for root, _, files in os.walk(group_dir):
                    for f in files:
                        zf.write(os.path.join(root, f), os.path.join(ch_obj.clean_chapter_number(), f))
                break
        else:
            continue
    with open(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename), "rb") as f:
        zip_file = f.read()
    return zip_file, zip_filename

def zip_chapter(series_slug, chapter):
    ch_obj = Chapter.objects.filter(series__slug=series_slug, chapter_number=chapter).first()
    chapter_dir = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", ch_obj.folder)
    groups = os.listdir(chapter_dir)
    chapter_group = None
    for group in settings.PREFERRED_SORT:
        if group in groups:
            chapter_group = group
            break
    else:
        return None
    chapter_pages = [os.path.join(chapter_dir, chapter_group, f) for f in os.listdir(os.path.join(chapter_dir, chapter_group))]
    zip_filename = f"{ch_obj.slug_chapter_number()}.zip"
    zf = zipfile.ZipFile(os.path.join(chapter_dir, zip_filename), "w")
    for fpath in chapter_pages:
        _, fname = os.path.split(fpath)
        zf.write(fpath, fname)
    zf.close()
    with open(os.path.join(chapter_dir, zip_filename), 'rb') as fh:
        zip_file = fh.read()
    return zip_file, zip_filename, fname
    