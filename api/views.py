import os
import json
import zipfile
from datetime import datetime, timezone
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
from reader.models import Series, Volume, Chapter, Group, ChapterIndex
from .api import series_data, series_data_cache, all_groups, random_chars, create_preview_pages, clear_series_cache, clear_pages_cache, zip_series, zip_chapter
from django.views.decorators.csrf import csrf_exempt


def get_series_data(request, series_slug):
    series_api_data = cache.get(f"series_api_data_{series_slug}")
    if not series_api_data:
        series_api_data, _ = series_data_cache(series_slug)
    return HttpResponse(json.dumps(series_api_data), content_type="application/json")

def series_data_hash(request, series_slug):
    series_api_hash = cache.get(f"series_api_hash_{series_slug}")
    if not series_api_hash:
        _, series_api_hash = series_data_cache(series_slug)
    return HttpResponse(json.dumps(cache.get(f"series_api_hash_{series_slug}")), content_type="application/json")

def get_all_series(request):
    all_series_data = cache.get(f"all_series_data")
    if not all_series_data:
        all_series = Series.objects.all().select_related("author", "artist")
        all_series_data = {}
        for series in all_series:
            vols = Volume.objects.filter(series=series).order_by('-volume_number')
            cover_vol_url = ""
            for vol in vols:
                if vol.volume_cover:
                    cover_vol_url = f"/media/{vol.volume_cover}"
                    break
            _, series_api_hash = series_data_cache(series.slug)
            all_series_data[series.name] = {"author": series.author.name, "artist": series.artist.name, "description": series.synopsis, "slug": series.slug, "cover": cover_vol_url, "groups": all_groups(), "series_data_hash": series_api_hash}
        cache.set("all_series_data", all_series_data, 3600 * 12)
    return HttpResponse(json.dumps(all_series_data), content_type="application/json")

def get_groups(request, series_slug):
    groups_data = cache.get(f"groups_data_{series_slug}")
    if not groups_data:
        groups_data = {str(ch.group.id) : ch.group.name for ch in Chapter.objects.filter(series__slug=series_slug).select_related('group')}
        cache.set(f"groups_data_{series_slug}", groups_data, 3600 * 12)
    return HttpResponse(json.dumps({"groups": groups_data}), content_type="application/json")

def get_all_groups(request):
    return HttpResponse(json.dumps(all_groups()), content_type="application/json")

def download_all_chapters(request, series_slug):
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, f"{series_slug}.zip")):
        zip_filename = f"{series_slug}.zip"
        with open(os.path.join(settings.MEDIA_ROOT, "manga", series_slug, zip_filename), "rb") as f:
            zip_file = f.read()
    else:
        zip_file, zip_filename = zip_series(series_slug)
    resp = HttpResponse(zip_file, content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def download_chapter(request, series_slug, chapter):
    ch_obj = Chapter.objects.get(series__slug=series_slug, chapter_number=chapter)
    chapter_dir = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", ch_obj.folder)
    if os.path.exists(os.path.join(chapter_dir, f"{ch_obj.slug_chapter_number()}.zip")):
        zip_filename = f"{ch_obj.slug_chapter_number()}.zip"
        with open(os.path.join(chapter_dir, f"{ch_obj.slug_chapter_number()}.zip"), "rb") as f:
            zip_file = f.read()
    else:
        zip_file, zip_filename, _ = zip_chapter(series_slug, chapter)
    resp = HttpResponse(zip_file, content_type="application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

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
            reupload = Chapter.objects.filter(chapter_number=chapter_number, series=series, group=group).first()
            if reupload:
                reupload.delete()
            else:
                uid = existing_chapter.folder
        Chapter.objects.create(chapter_number=chapter_number, group=group, series=series, folder=uid, title=request.POST["chapterTitle"], volume=request.POST["volumeNumber"], uploaded_on=datetime.utcnow().replace(tzinfo=timezone.utc))
        chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", series_slug, "chapters", uid)
        group_folder = str(group.id)
        if os.path.exists(os.path.join(chapter_folder, group_folder)):
            return HttpResponse(JsonResponse({"response": "Error: This chapter by this group already exists but wasn't recorded in the database. Chapter has been recorded but not uploaded."}))
        os.makedirs(os.path.join(chapter_folder, group_folder))
        os.makedirs(os.path.join(chapter_folder, f"{group_folder}_shrunk"))
        os.makedirs(os.path.join(chapter_folder, f"{group_folder}_shrunk_blur"))
        with zipfile.ZipFile(request.FILES["chapterPages"]) as zip_file:
            all_pages = sorted(zip_file.namelist())
            padding = len(str(len(all_pages)))
            for idx, page in enumerate(all_pages):
                extension = page.rsplit(".", 1)[1]
                page_file = f"{str(idx+1).zfill(padding)}.{extension}"
                with open(os.path.join(chapter_folder, group_folder, page_file), "wb") as f:
                    f.write(zip_file.read(page))
                create_preview_pages(chapter_folder, group_folder, page_file)
                zip_chapter(series.slug, chapter_number)
                zip_series(series.slug)
        return HttpResponse(json.dumps({"response": "success"}), content_type="application/json")

def get_volume_covers(request, series_slug):
    if request.POST:
        covers = cache.get(f"vol_covers_{series_slug}")
        if not covers:
            series = Series.objects.get(slug=series_slug)
            volume_covers = Volume.objects.filter(series=series).order_by('volume_number').values_list('volume_number', 'volume_cover')
            covers = {"covers": [[cover[0], f"/media/{cover[1]}"] for cover in volume_covers]}
            cache.set(f"vol_covers_{series_slug}", covers)
        return HttpResponse(json.dumps(covers), content_type="application/json")

@csrf_exempt
def search_index(request, series_slug):
    if request.POST:
        search_query = request.POST["searchQuery"]
        search_results = {}
        for word in set(search_query.split()[:20]):
            word_query = ChapterIndex.objects.filter(word__startswith=word.upper())
            search_results[word] = {}
            for word_obj in word_query:
                chapter_and_pages = word_obj.chapter_and_pages
                search_results[word][word_obj.word] = chapter_and_pages
        return HttpResponse(json.dumps(search_results), content_type="application/json")

def clear_cache(request):
    if request.POST and request.user and request.user.is_staff:
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
