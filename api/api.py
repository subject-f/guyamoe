import json
import os
import random
import shutil
import subprocess
import zipfile
from ast import literal_eval
from datetime import datetime, timezone

from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from PIL import Image, ImageFilter

from reader.models import Chapter, ChapterIndex, Group, Series, Volume


def all_chapter_data_etag(request):
    etag = cache.get("all_chapter_data_etag")
    if not etag:
        obj = Chapter.objects.order_by("-uploaded_on").first()
        etag = str(obj.updated_on or obj.uploaded_on)
        cache.set("all_chapter_data_etag", etag, 600)
    return etag


def chapter_data_etag(request, series_slug):
    etag = cache.get(f"{series_slug}_chapter_data_etag")
    if not etag:
        obj = (
            Chapter.objects.filter(series=Series.objects.get(slug=series_slug))
            .order_by("-uploaded_on")
            .first()
        )
        etag = str(obj.updated_on or obj.uploaded_on)
        cache.set(f"{series_slug}_chapter_data_etag", etag, 600)
    return etag


def series_data(series_slug):
    series = Series.objects.filter(slug=series_slug).first()
    if not series:
        raise Http404("Page not found.")
    chapters = Chapter.objects.filter(series=series).select_related("group")
    chapters_dict = {}
    groups_dict = {}
    for chapter in chapters:
        chapter_media_path = os.path.join(
            settings.MEDIA_ROOT, "manga", series_slug, "chapters", chapter.folder
        )
        ch_clean = Chapter.clean_chapter_number(chapter)
        groups_dict[str(chapter.group.id)] = chapter.group.name
        query_string = "" if not chapter.version else f"?v{chapter.version}"
        if ch_clean in chapters_dict:
            chapters_dict[ch_clean]["groups"][str(chapter.group.id)] = sorted(
                [
                    u + query_string
                    for u in os.listdir(
                        os.path.join(chapter_media_path, str(chapter.group.id))
                    )
                ]
            )
            chapters_dict[ch_clean]["release_date"][str(chapter.group.id)] = int(
                chapter.uploaded_on.timestamp()
            )
        else:
            chapters_dict[ch_clean] = {
                "volume": str(chapter.volume),
                "title": chapter.title,
                "folder": chapter.folder,
                "groups": {
                    str(chapter.group.id): sorted(
                        [
                            u + query_string
                            for u in os.listdir(
                                os.path.join(chapter_media_path, str(chapter.group.id))
                            )
                        ]
                    )
                },
                "release_date": {
                    str(chapter.group.id): int(chapter.uploaded_on.timestamp())
                },
            }
        if chapter.preferred_sort:
            try:
                chapters_dict[ch_clean]["preferred_sort"] = literal_eval(
                    chapter.preferred_sort
                )
            except Exception:
                pass
    vols = Volume.objects.filter(series=series).order_by("-volume_number")
    cover_vol_url = ""
    for vol in vols:
        if vol.volume_cover:
            cover_vol_url = f"/media/{vol.volume_cover}"
            break
    return {
        "slug": series_slug,
        "title": series.name,
        "description": series.synopsis,
        "author": series.author.name,
        "artist": series.artist.name,
        "groups": groups_dict,
        "cover": cover_vol_url,
        "preferred_sort": literal_eval(series.preferred_sort)
        if series.preferred_sort
        else [],
        "chapters": chapters_dict,
        "next_release_page": series.next_release_page,
        "next_release_time": series.next_release_time.timestamp()
        if series.next_release_time
        else None,
        "next_release_html": series.next_release_html,
    }


def series_data_cache(series_slug):
    series_api_data = series_data(series_slug)
    cache.set(f"series_api_data_{series_slug}", series_api_data, 3600 * 48)
    return series_api_data


def all_groups():
    groups_data = cache.get("all_groups_data")
    if not groups_data:
        groups_data = {str(group.id): group.name for group in Group.objects.all()}
        cache.set("all_groups_data", groups_data, 3600 * 12)
    return groups_data


def random_chars():
    return "".join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=8))


def delete_chapter_pages_if_exists(folder_path, clean_chapter_number, group_id):
    group_id = str(group_id)
    shutil.rmtree(os.path.join(folder_path, group_id), ignore_errors=True)
    shutil.rmtree(os.path.join(folder_path, f"{group_id}_shrunk"), ignore_errors=True)
    shutil.rmtree(
        os.path.join(folder_path, f"{group_id}_shrunk_blur"), ignore_errors=True
    )
    if os.path.exists(os.path.join(folder_path, f"{str(clean_chapter_number)}.zip")):
        os.remove(os.path.join(folder_path, f"{str(clean_chapter_number)}.zip"))


def create_chapter_obj(
    chapter: float, group: Group, series: Series, latest_volume: int, title: str,
):
    update = False
    chapter_number = chapter
    existing_chapter = Chapter.objects.filter(
        chapter_number=chapter_number, series=series
    ).first()
    chapter_folder_numb = f"{int(chapter_number):04}"
    chapter_folder_numb += (
        f"-{str(chapter_number).rsplit('.')[1]}_"
        if not str(chapter_number).endswith("0")
        else "_"
    )

    if not existing_chapter:
        uid = chapter_folder_numb + random_chars()
    else:
        uid = existing_chapter.folder
    chapter_folder = os.path.join(
        settings.MEDIA_ROOT, "manga", series.slug, "chapters", uid
    )
    group_folder = str(group.id)

    # If chapter exists, see if release by group exists. if it does, delete the group's chapter pages
    if existing_chapter:
        ch_obj = Chapter.objects.filter(
            chapter_number=chapter_number, series=series, group=group
        ).first()
        if ch_obj:
            delete_chapter_pages_if_exists(
                chapter_folder, existing_chapter.clean_chapter_number(), group_folder,
            )
            update = True

    # Create the chapter model for the group if it didn't exist.
    if not existing_chapter or not ch_obj:
        ch_obj = Chapter.objects.create(
            chapter_number=chapter_number,
            group=group,
            series=series,
            folder=uid,
            title=title,
            volume=latest_volume,
            uploaded_on=datetime.utcnow().replace(tzinfo=timezone.utc),
        )
    chapter_folder = os.path.join(
        settings.MEDIA_ROOT, "manga", series.slug, "chapters", uid
    )
    os.makedirs(os.path.join(chapter_folder, str(group.id)))
    os.makedirs(os.path.join(chapter_folder, f"{str(group.id)}_shrunk"))
    os.makedirs(os.path.join(chapter_folder, f"{str(group.id)}_shrunk_blur"))
    clear_pages_cache()
    return ch_obj, chapter_folder, str(group.id), update


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
    blur.thumbnail((blur.width / 8, blur.height / 8), Image.ANTIALIAS)
    shrunk.save(
        os.path.join(chapter_folder, f"{group_folder}_shrunk", page_file),
        "JPEG",
        quality=100,
        optimize=True,
        progressive=True,
    )
    blur = blur.filter(ImageFilter.GaussianBlur(radius=2))
    blur.save(
        os.path.join(chapter_folder, f"{group_folder}_shrunk_blur", page_file),
        "JPEG",
        quality=100,
        optimize=True,
        progressive=True,
    )


def get_chapter_preferred_sort(chapter):
    preferred_sort = None
    for ch in Chapter.objects.filter(
        chapter_number=chapter.chapter_number, series=chapter.series
    ):
        if ch.preferred_sort:
            try:
                preferred_sort = literal_eval(preferred_sort)
                break
            except Exception:
                pass
    if not preferred_sort:
        try:
            preferred_sort = (
                literal_eval(chapter.series.preferred_sort)
                if chapter.series.preferred_sort
                else None
            )
        except Exception:
            pass
    return preferred_sort


def index_chapter(chapter):
    if hasattr(settings, "OCR_SCRIPT_PATH") and os.path.exists(
        settings.OCR_SCRIPT_PATH
    ):
        ch_slug = chapter.slug_chapter_number()
        group_folder = str(chapter.group.id)
        preferred_sort = get_chapter_preferred_sort(chapter)
        if preferred_sort:
            if str(chapter.group.id) in preferred_sort:
                curr_chap_index_priority = preferred_sort.index(str(chapter.group.id))
            else:
                curr_chap_index_priority = len(preferred_sort)
            all_chap_groups = [
                ch.group.id
                for ch in Chapter.objects.filter(
                    chapter_number=chapter.chapter_number, series=chapter.series
                )
                if ch.group != chapter.group
            ]

            # if chapter by other group(s) exists, check if the new chapter has a higher priority on the preferred_sort list. only index if it is.
            index_to_beat = len(preferred_sort)
            if all_chap_groups:
                for group in all_chap_groups:
                    if str(group) in preferred_sort:
                        group_index = preferred_sort.index(str(group))
                        if group_index < index_to_beat:
                            index_to_beat = group_index
                if curr_chap_index_priority > index_to_beat:
                    return
        print("Deleting old chapter index from db.")
        for index in ChapterIndex.objects.filter(series=chapter.series):
            word_dict = json.loads(index.chapter_and_pages)
            if ch_slug in word_dict:
                del word_dict[ch_slug]
                index.chapter_and_pages = json.dumps(word_dict)
                index.save()
        print("Finished deleting old chapter index from db.")
        print("Indexing chapter pages...")
        chapter_folder = os.path.join(
            settings.MEDIA_ROOT,
            "manga",
            chapter.series.slug,
            "chapters",
            chapter.folder,
        )
        subprocess.Popen(
            f"bash {settings.OCR_SCRIPT_PATH} {chapter_folder}/{group_folder} {chapter.clean_chapter_number()} {chapter.clean_chapter_number()}_{chapter.series.id} {chapter.series.slug}".split()
        )


def chapter_post_process(chapter, is_update=True):
    chapter_folder = os.path.join(
        settings.MEDIA_ROOT, "manga", chapter.series.slug, "chapters", chapter.folder
    )
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
    if is_update:
        chapter.version = chapter.version + 1 if chapter.version else 2
        chapter.updated_on = datetime.utcnow().replace(tzinfo=timezone.utc)
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


def zip_chapter(series_slug, chapter, group):
    ch_obj = Chapter.objects.filter(
        series__slug=series_slug, chapter_number=chapter, group=group
    ).first()
    chapter_dir = os.path.join(
        settings.MEDIA_ROOT, "manga", series_slug, "chapters", ch_obj.folder
    )
    chapter_pages = [
        os.path.join(chapter_dir, str(group.id), f)
        for f in os.listdir(os.path.join(chapter_dir, str(group.id)))
    ]
    zip_filename = f"{ch_obj.group.id}_{ch_obj.slug_chapter_number()}.zip"
    zf = zipfile.ZipFile(os.path.join(chapter_dir, zip_filename), "w")
    for fpath in chapter_pages:
        _, fname = os.path.split(fpath)
        zf.write(fpath, fname)
    zf.close()
    with open(os.path.join(chapter_dir, zip_filename), "rb") as fh:
        zip_file = fh.read()
    return zip_file, zip_filename, fname
