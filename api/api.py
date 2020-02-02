import random
import os
import json
import zipfile
import requests
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

def md_series_page_data(series_id):
    series_page_dt = cache.get(f"series_page_dt_{series_id}")
    if not series_page_dt:
        resp = get_md_data(f"https://mangadex.org/api/?id={series_id}&type=manga")
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            chapter_list = []
            latest_chap_id = next(iter(api_data["chapter"]))
            date = datetime.utcfromtimestamp(api_data["chapter"][latest_chap_id]["timestamp"])
            last_updated = (api_data["chapter"][latest_chap_id]["chapter"], datetime.utcfromtimestamp(api_data["chapter"][latest_chap_id]["timestamp"]).strftime("%y/%m/%d"))
            chapter_dict = {}
            for ch in api_data["chapter"]:
                try:
                    float(api_data["chapter"][ch]["chapter"])
                except ValueError:
                    continue
                if api_data["chapter"][ch]["lang_code"] == "gb":
                    date = datetime.utcfromtimestamp(api_data["chapter"][ch]["timestamp"])
                    if api_data["chapter"][ch]["chapter"] in chapter_dict:
                        chapter_dict[api_data["chapter"][ch]["chapter"]] = [api_data["chapter"][ch]["chapter"], api_data["chapter"][ch]["title"], api_data["chapter"][ch]["chapter"].replace(".", "-"), "Multiple Groups", [date.year, date.month-1, date.day, date.hour, date.minute, date.second], api_data["chapter"][ch]["volume"], ch]
                    else:
                        chapter_dict[api_data["chapter"][ch]["chapter"]] = [api_data["chapter"][ch]["chapter"], api_data["chapter"][ch]["title"], api_data["chapter"][ch]["chapter"].replace(".", "-"), api_data["chapter"][ch]["group_name"], [date.year, date.month-1, date.day, date.hour, date.minute, date.second], api_data["chapter"][ch]["volume"], ch]
            chapter_list = [x[1] for x in sorted(chapter_dict.items(), key=lambda m: float(m[0]), reverse=True)]
            series_page_dt = {
                "series": api_data["manga"]["title"],
                "series_id": api_data["manga"]["description"],
                "slug": series_id,
                "cover_vol_url": "https://mangadex.org" + api_data["manga"]["cover_url"],
                "synopsis": api_data["manga"]["description"], 
                "author": api_data["manga"]["author"],
                "artist": api_data["manga"]["artist"],
                "last_added": last_updated,
                "chapter_list": chapter_list,
                "volume_list": sorted([], key=lambda m: m[0], reverse=True)
            }
            cache.set(f"series_page_dt_{series_id}", series_page_dt, 60)
        else:
            return None
    return series_page_dt

def md_series_data(series_id):
    data = cache.get(f"series_dt_{series_id}")
    if not data:
        resp = get_md_data(f"https://mangadex.org/api/?id={series_id}&type=manga")
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            groups_dict = {}
            chapters_dict = {}
            for chapter in api_data["chapter"]:
                groups_dict[api_data["chapter"][chapter]["group_id"]] = api_data["chapter"][chapter]["group_name"]
                if api_data["chapter"][chapter]["lang_code"] == "gb":
                    if api_data["chapter"][chapter]["chapter"] in chapters_dict:
                        if not chapters_dict[api_data["chapter"][chapter]["chapter"]]["volume"]:
                            chapters_dict[api_data["chapter"][chapter]["chapter"]]["volume"] = api_data["chapter"][chapter]["volume"]
                        if not chapters_dict[api_data["chapter"][chapter]["chapter"]]["title"]:
                            chapters_dict[api_data["chapter"][chapter]["chapter"]]["title"] = api_data["chapter"][chapter]["title"]
                        chapters_dict[api_data["chapter"][chapter]["chapter"]]["groups"][api_data["chapter"][chapter]["group_id"]] = chapter
                    else:
                        chapters_dict[api_data["chapter"][chapter]["chapter"]] = {
                            # "chapter_id": chapter,
                            "volume": api_data["chapter"][chapter]["volume"],
                            "title": api_data["chapter"][chapter]["title"],
                            "groups": {
                                api_data["chapter"][chapter]["group_id"]: chapter
                            }
                        }
            for chapter in chapters_dict:
                if not chapters_dict[chapter]["volume"]:
                    chapters_dict[chapter]["volume"] = "Uncategorized"
            data = {
                "slug": series_id, "title": api_data["manga"]["title"], "description": api_data["manga"]["description"], 
                "author": api_data["manga"]["author"], "artist": api_data["manga"]["artist"], "groups": groups_dict,
                "cover": api_data["manga"]["cover_url"], "preferred_sort": settings.PREFERRED_SORT, "chapters": chapters_dict
            }
            cache.set(f"series_dt_{series_id}", data, 60)
        else:
            return None
    return data

def md_chapter_info(chapter_id):
    chapter_info = cache.get(f"chapter_dt_{chapter_id}")
    if not chapter_info:
        resp = get_md_data(f"https://mangadex.org/api/?id={chapter_id}&server=null&type=chapter")
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            chapter_pages = [f"{api_data['server']}{api_data['hash']}/{page}" for page in api_data["page_array"]]
            chapter_info = {"pages": chapter_pages, "series_id": api_data["manga_id"], "chapter": api_data["chapter"]}
            cache.set(f"chapter_dt_{chapter_id}", chapter_info, 60)
        else:
            return None
    return chapter_info

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
    with open(os.path.join(chapter_dir, zip_filename), "rb") as fh:
        zip_file = fh.read()
    return zip_file, zip_filename, fname

def nh_series_data(series_id):
    data = cache.get(f"nh_series_dt_{series_id}")
    if not data:
        nh_series_api = f"https://nhentai.net/api/gallery/{series_id}"
        headers = {
            'Referer': 'https://nhentai.net',
            'User-Agent': 'Mozilla Firefox Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0.'
        }
        resp = requests.get(nh_series_api, headers=headers)
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)

            artist = api_data["scanlator"]
            group = api_data["scanlator"]
            lang_list = []
            tag_list = []
            for tag in api_data["tags"]:
                if tag["type"] == "artist":
                    artist = tag["name"]
                elif tag["type"] == "group":
                    group = tag["name"]
                elif tag["type"] == "language":
                    lang_list.append(tag["name"])
                elif tag["type"] == "tag":
                    tag_list.append(tag["name"])

            pages_list = []
            for p, t in enumerate(api_data["images"]["pages"]):
                file_format = "jpg"
                if t["t"] == "p":
                    file_format = "png"
                if t["t"] == "g":
                    file_format = "gif"
                pages_list.append(f"https://i.nhentai.net/galleries/{api_data['media_id']}/{p + 1}.{file_format}")

            groups_dict = {"1": group or "N-Hentai"}
            chapters_dict = {
                "1" : {
                    "volume": "1", "title": api_data["title"]["pretty"] or api_data["title"]["english"],
                    "groups": {
                        "1": pages_list
                    }
                }
            }

            data = {
                "slug": series_id, "title": api_data["title"]["pretty"] or api_data["title"]["english"],
                "description": api_data["title"]["english"], "group": group, "artist": artist, "groups": groups_dict,
                "tags": tag_list, "lang": ", ".join(lang_list), "chapters": chapters_dict,
                "cover": f"https://t.nhentai.net/galleries/{api_data['media_id']}/cover.{'jpg' if api_data['images']['cover']['t'] == 'j' else 'png'}",
            }
            cache.set(f"nh_series_dt_{series_id}", data, 60)
        else:
            return None
    return data

def get_md_data(url):
    headers = {
        'Referer': 'https://mangadex.org',
        'User-Agent': 'Mozilla Firefox Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0.'
    }
    return requests.get(url, headers=headers)
