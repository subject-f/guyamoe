from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound
from reader.models import Series, Chapter
import json
import os


def series_data(request, series_slug):
    series = Series.objects.get(slug=series_slug)
    chapters = Chapter.objects.filter(series=series)
    chapters_dict = {}
    for chapter in chapters:
        chapter_media_path = f"{settings.MEDIA_ROOT}\\manga\\{'Kaguya-Wants-To-Be-Confessed-To'}\\{Chapter.slug_chapter_number(chapter)}"
        chapters_dict[Chapter.clean_chapter_number(chapter)] = {
            "volume": str(chapter.volume), 
            "title": chapter.title,
            "pagecount": chapter.page_count,
            "pages": sorted(os.listdir(chapter_media_path)) if os.path.exists(chapter_media_path) else []
        }
    data = {"slug": series_slug, "title": series.name, "chapters": chapters_dict}
    return HttpResponse(json.dumps(data), content_type="application/json")