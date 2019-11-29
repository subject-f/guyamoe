from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from reader.models import Series, Chapter

class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return ['site-home', 'site-about']

    def location(self, item):
        return reverse(item)

class SeriesSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    protocol = 'https'

    def items(self):
        return Series.objects.all()

class ChapterSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.4
    protocol = 'https'

    def items(self):
        return Chapter.objects.filter(series__isnull=False).order_by('series__id', '-chapter_number')