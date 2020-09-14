import hashlib
import json
import os
import time
import zipfile
from datetime import datetime

from discord import Embed, RequestsWebhookAdapter, Webhook
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt

from reader.models import Chapter, ChapterIndex, Group, Series, Volume
from reader.users_cache_lib import get_user_ip

from .api import (
    all_groups,
    chapter_post_process,
    clear_pages_cache,
    clear_series_cache,
    create_chapter_obj,
    get_chapter_preferred_sort,
    series_data_cache,
    zip_chapter,
)


@cache_control(public=True, max_age=30, s_maxage=30)
def get_series_data(request, series_slug):
    series_api_data = cache.get(f"series_api_data_{series_slug}")
    if not series_api_data:
        series_api_data = series_data_cache(series_slug)
    return HttpResponse(json.dumps(series_api_data), content_type="application/json")


@cache_control(public=True, max_age=900, s_maxage=900)
def get_all_series(request):
    all_series_data = cache.get("all_series_data")
    if not all_series_data:
        all_series = Series.objects.all().select_related("author", "artist")
        all_series_data = {}
        for series in all_series:
            vols = Volume.objects.filter(series=series).order_by("-volume_number")
            cover_vol_url = ""
            for vol in vols:
                if vol.volume_cover:
                    cover_vol_url = f"/media/{vol.volume_cover}"
                    break
            chapters = Chapter.objects.filter(series=series)
            last_updated = None
            for ch in chapters:
                if not last_updated or ch.uploaded_on > last_updated:
                    last_updated = ch.uploaded_on
            all_series_data[series.name] = {
                "author": series.author.name,
                "artist": series.artist.name,
                "description": series.synopsis,
                "slug": series.slug,
                "cover": cover_vol_url,
                "groups": all_groups(),
                "last_updated": int(datetime.timestamp(last_updated))
                if last_updated
                else 0,
            }
        cache.set("all_series_data", all_series_data, 3600 * 12)
    return HttpResponse(json.dumps(all_series_data), content_type="application/json")


@cache_control(public=True, max_age=7200, s_maxage=7200)
def get_groups(request, series_slug):
    groups_data = cache.get(f"groups_data_{series_slug}")
    if not groups_data:
        groups_data = {
            str(ch.group.id): ch.group.name
            for ch in Chapter.objects.filter(series__slug=series_slug).select_related(
                "group"
            )
        }
        cache.set(f"groups_data_{series_slug}", groups_data, 3600 * 12)
    return HttpResponse(
        json.dumps({"groups": groups_data}), content_type="application/json"
    )


@cache_control(public=True, max_age=7200, s_maxage=7200)
def get_all_groups(request):
    return HttpResponse(json.dumps(all_groups()), content_type="application/json")


# @cache_control(public=True, max_age=43200, s_maxage=43200)
# def download_volume(request, series_slug, volume):
#     zip_filename = f"{series_slug}_vol_{volume}.zip"
#     zip_path = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename)
#     if os.path.exists(zip_path) and not (
#         time.time() - os.stat(zip_path).st_mtime > (3600 * 8)
#     ):
#         with open(
#             os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename), "rb"
#         ) as fh:
#             zip_file = fh.read()
#     else:
#         zip_file, zip_filename = zip_volume(series_slug, volume)
#     resp = HttpResponse(zip_file, content_type="application/x-zip-compressed")
#     resp["Content-Disposition"] = "attachment; filename=%s" % zip_filename
#     return resp


@cache_control(public=True, max_age=21600, s_maxage=21600)
def download_chapter(request, series_slug, chapter):
    group = request.GET.get("group", None)
    chapter_number = float(chapter.replace("-", "."))
    if not group:
        ch_qs = Chapter.objects.filter(
            series__slug=series_slug, chapter_number=chapter_number
        )
        if not ch_qs:
            return HttpResponseBadRequest()
        preferred_sort = get_chapter_preferred_sort(ch_qs.first())
        if preferred_sort:
            for group in preferred_sort:
                ch_obj = ch_qs.filter(group__id=int(group)).first()
                if ch_obj:
                    break
            if not ch_obj:
                ch_obj = ch_qs.first()
    else:
        if not group.isdigit():
            return HttpResponseBadRequest()
        ch_obj = Chapter.objects.get(
            series__slug=series_slug,
            chapter_number=chapter_number,
            group__id=int(group),
        )
    group = str(ch_obj.group.id)
    chapter_dir = os.path.join(
        settings.MEDIA_ROOT, "manga", series_slug, "chapters", ch_obj.folder
    )
    zip_chapter_file = f"{group}_{ch_obj.slug_chapter_number()}.zip"
    zip_path = os.path.join(chapter_dir, zip_chapter_file)
    if os.path.exists(zip_path) and not (
        time.time() - os.stat(zip_path).st_mtime > (3600 * 8)
    ):
        with open(os.path.join(chapter_dir, zip_chapter_file), "rb") as f:
            zip_file = f.read()
    else:
        zip_file, _, _ = zip_chapter(series_slug, chapter_number, ch_obj.group)
    resp = HttpResponse(zip_file, content_type="application/x-zip-compressed")
    resp[
        "Content-Disposition"
    ] = f"attachment; filename={ch_obj.slug_chapter_number()}.zip"
    return resp


def upload_new_chapter(request, series_slug):
    if request.method == "POST" and request.user and request.user.is_staff:
        group = Group.objects.get(name=request.POST["scanGroup"])
        series = Series.objects.get(slug=series_slug)
        chapter_number = float(request.POST["chapterNumber"])
        volume = request.POST["volumeNumber"]
        title = request.POST["chapterTitle"]
        ch_obj, chapter_folder, group_folder, is_update = create_chapter_obj(
            chapter_number, group, series, volume, title
        )
        os.makedirs(os.path.join(chapter_folder, group_folder))
        with zipfile.ZipFile(request.FILES["chapterPages"]) as zip_file:
            zipped_pages = zip_file.namelist()
            if all(
                [x.split(" ", 1)[0].split(".", 1)[0].isdigit() for x in zipped_pages]
            ):
                all_pages = sorted(
                    zipped_pages, key=lambda x: int(x.split(" ", 1)[0].split(".", 1)[0])
                )
            else:
                all_pages = sorted(zipped_pages)
            padding = len(str(len(all_pages)))
            for idx, page in enumerate(all_pages):
                extension = page.rsplit(".", 1)[1]
                page_file = f"{str(idx+1).zfill(padding)}.{extension}"
                with open(
                    os.path.join(chapter_folder, group_folder, page_file), "wb"
                ) as f:
                    f.write(zip_file.read(page))
        chapter_post_process(ch_obj, is_update=is_update)
        return HttpResponse(
            json.dumps({"response": "success"}), content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"response": "failure"}), content_type="application/json"
        )


@csrf_exempt
@cache_control(public=True, max_age=3600, s_maxage=3600)
def get_volume_covers(request, series_slug):
    if request.method == "POST":
        covers = cache.get(f"vol_covers_{series_slug}")
        if not covers:
            series = Series.objects.get(slug=series_slug)
            volume_covers = (
                Volume.objects.filter(series=series)
                .order_by("volume_number")
                .values_list("volume_number", "volume_cover")
            )
            covers = {
                "covers": [
                    [
                        cover[0],
                        f"/media/{str(cover[1])}",
                        f"/media/{str(cover[1]).rsplit('.', 1)[0]}.webp",
                    ]
                    for cover in volume_covers
                    if cover[1]
                ]
            }
            cache.set(f"vol_covers_{series_slug}", covers)
        return HttpResponse(json.dumps(covers), content_type="application/json")
    else:
        return HttpResponse(json.dumps({}), content_type="application/json")


@csrf_exempt
def search_index(request, series_slug):
    if request.method == "POST":
        series = Series.objects.get(slug=series_slug)
        search_query = request.POST["searchQuery"]
        search_results = {}
        for word in set(search_query.split()[:20]):
            word_query = ChapterIndex.objects.filter(
                word__startswith=word.upper(), series=series
            )
            search_results[word] = {}
            for word_obj in word_query:
                chapter_and_pages = json.loads(word_obj.chapter_and_pages)
                search_results[word][word_obj.word] = chapter_and_pages
        return HttpResponse(json.dumps(search_results), content_type="application/json")
    else:
        return HttpResponse(json.dumps({}), content_type="application/json")


@csrf_exempt
def clear_cache(request):
    if request.method == "POST" and request.user and request.user.is_staff:
        if request.POST["clear_type"] == "all":
            clear_pages_cache()
            response = "Cleared all cache"
        elif request.POST["clear_type"] == "chapter":
            for series_slug in Series.objects.all().values_list("slug"):
                clear_series_cache(series_slug)
            response = "Cleared series cache"
        else:
            response = "Not a valid option"
        return HttpResponse(
            json.dumps({"response": response}), content_type="application/json"
        )
    else:
        return HttpResponse(json.dumps({}), content_type="application/json")


@csrf_exempt
def black_hole_mail(request):
    if request.method == "POST":
        text = request.POST["text"]
        user_ip = get_user_ip(request)
        user_sent_count = cache.get(f"mail_user_ip_{user_ip}")
        if not user_sent_count:
            cache.set(f"mail_user_ip_{user_ip}", 1, 30)
        else:
            user_sent_count += 1
            if user_sent_count > 4:
                return HttpResponse(
                    json.dumps({"error": "Error: sending mail too frequently."}),
                    content_type="application/json",
                )
            else:
                cache.set(f"mail_user_ip_{user_ip}", user_sent_count, 30)
        if len(text) > 2000:
            return HttpResponse(
                json.dumps(
                    {"error": "Error: message too long. can only send 2000 characters."}
                ),
                content_type="application/json",
            )
        try:
            webhook = Webhook.partial(
                settings.MAIL_DISCORD_WEBHOOK_ID,
                settings.MAIL_DISCORD_WEBHOOK_TOKEN,
                adapter=RequestsWebhookAdapter(),
            )
            em = Embed(
                color=0x000000,
                title="Black Hole",
                description=f"⚫ You've got guyamail! 📬\n\n{text}",
                timestamp=datetime.utcnow(),
            )
            em.set_footer(
                text=f"IP hash: {hashlib.md5(user_ip.encode()).hexdigest()[:32]}"
            )
            webhook.send(content=None, embed=em, username="Guya.moe")
        except (AttributeError, NameError):
            feedback_folder = os.path.join(settings.MEDIA_ROOT, "feedback")
            os.makedirs(feedback_folder, exist_ok=True)
            feedback_file = str(int(datetime.utcnow().timestamp()))
            with open(os.path.join(feedback_folder, f"{feedback_file}.txt"), "w") as f:
                f.write(text)
        return HttpResponse(
            json.dumps({"success": "Mail successfully crossed the event horizon"}),
            content_type="application/json",
        )
