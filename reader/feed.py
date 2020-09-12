from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.shortcuts import reverse
from django.utils.feedgenerator import DefaultFeed

from reader.models import Chapter, Series


class CorrectMimeTypeFeed(DefaultFeed):
    content_type = "application/xml; charset=utf-8"


class AllChaptersFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    link = "/all/"
    title = "All Chapter updates"
    description = "Latest chapter updates"

    def items(self):
        return Chapter.objects.order_by("-uploaded_on")

    def item_title(self, item):
        return f"{item.series.name} - Chapter {Chapter.clean_chapter_number(item)}"

    def item_link(self, item):
        return f"https://guya.moe/read/manga/{item.series.slug}/{Chapter.slug_chapter_number(item)}/1"

    def item_description(self, item):
        return f"Group: {item.group.name} - Title {item.title}"

    def item_pubdate(self, item):
        return item.uploaded_on


class SeriesChaptersFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    title = "Series Chapter updates"
    description = "Latest chapter updates"

    def get_object(self, request, series_slug):
        return Series.objects.get(slug=series_slug)

    def title(self, obj):
        return obj.name

    def link(self, obj):
        return f"https://guya.moe/read/manga/{obj.slug}/"

    def description(self, obj):
        return obj.synopsis

    def item_title(self, obj):
        return f"{obj.series.name} - Chapter {Chapter.clean_chapter_number(obj)}"

    def item_link(self, obj):
        return f"https://guya.moe/read/manga/{obj.series.slug}/{Chapter.slug_chapter_number(obj)}/1"

    def item_description(self, obj):
        return f"Group: {obj.group.name} - Title {obj.title}"

    def items(self, obj):
        return Chapter.objects.filter(series=obj).order_by("-uploaded_on")

    def item_pubdate(self, item):
        return item.uploaded_on
