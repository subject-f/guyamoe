from django.core.cache import cache
from django.shortcuts import render
from .models import Page
import re


def content(request, page_url):
    page = Page.objects.get(page_url=page_url)
    return render(request, 'misc/misc.html', {'content': page.content })

def misc_pages(request):
    pages = cache.get("misc_pages")
    if not pages:
        pages = Page.objects.all().order_by('-date').values_list('page_title', 'page_url')
        print(pages)
        cache.set("misc_pages", pages, 3600 * 8)
    print(pages)
    return render(request, 'misc/misc_pages.html', {'pages': pages})