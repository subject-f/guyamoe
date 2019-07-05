from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound
from .models import Series, Chapter
import os

def series_info(request, series_slug):
    series = get_object_or_404(Series, slug=series_slug)
    chapters = Chapter.objects.filter(series=series)
    chapter_list = sorted([[ch.clean_chapter_number(), ch.title, ch.slug_chapter_number(), ch.group, ch.uploaded_on] for ch in chapters], key=lambda m: float(m[0]), reverse=True)
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