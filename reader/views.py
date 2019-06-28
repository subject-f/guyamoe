from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseNotFound
from .models import Series, Chapter
import os


def reader(request, series_slug, chapter, page):
    slug_chapter_numb = chapter.replace("-", ".")
    ch_obj = get_object_or_404(Chapter, series__slug=series_slug, chapter_number=slug_chapter_numb)
    return render(request, 'reader/reader.html', {})