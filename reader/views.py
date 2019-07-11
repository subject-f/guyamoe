from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound
from .models import Series, Chapter
from datetime import datetime, timedelta, timezone
import os

def series_info(request, series_slug):
    series = get_object_or_404(Series, slug=series_slug)
    chapters = Chapter.objects.filter(series=series)
    chapter_list = []
    for chapter in chapters:
        upload_date = chapter.uploaded_on
        upload_time = (datetime.utcnow().replace(tzinfo=timezone.utc) - upload_date).total_seconds()
        days = upload_time // (24 * 3600)
        upload_time = upload_time % (24 * 3600)
        hours = upload_time // 3600
        upload_time %= 3600
        minutes = upload_time // 60
        upload_time %= 60
        seconds = upload_time
        if days == 0 and hours == 0 and minutes == 0:
            upload_date = f"{int(seconds)} seconds ago"
        elif days == 0 and hours == 0:
            upload_date = f"{int(minutes)} mins ago"
        elif days == 0:
            upload_date = f"{int(hours)} hours ago"
        elif days < 7:
            upload_date = f"{int(days)} days ago"
        else:
            upload_date.strftime("%Y-%m-%d")
        chapter_list.append([chapter.clean_chapter_number(), chapter.title, chapter.slug_chapter_number(), chapter.group.name, upload_date, chapter.volume])
    chapter_list.sort(key=lambda m: float(m[0]), reverse=True)
    return render(request, 'reader/series_info.html', {
            "series": series.name, 
            "slug": series.slug, 
            "synopsis": series.synopsis, 
            "author": series.author.name,
            "artist": series.artist.name,
            "chapter_list": chapter_list,
            "is_mod": request.user.is_staff
        })


def reader(request, series_slug, chapter, page):
    slug_chapter_numb = chapter.replace("-", ".")
    _ = get_object_or_404(Chapter, series__slug=series_slug, chapter_number=slug_chapter_numb)
    return render(request, 'reader/reader.html', {})