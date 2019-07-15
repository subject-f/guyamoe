from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from datetime import datetime, timezone
import os

class HitCount(models.Model):
    content = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    hits = models.PositiveIntegerField(('Hits'), default=0)


class Person(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Create your models here.
class Series(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, max_length=200)
    author = models.ForeignKey(Person, blank=True, null=True, on_delete=models.SET_NULL, related_name='series_author')
    artist = models.ForeignKey(Person, blank=True, null=True, on_delete=models.SET_NULL, related_name='series_artist')
    synopsis = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


def path_file_name(instance, filename):
    return os.path.join("manga", instance.series.slug, "volume_covers", str(instance.volume_number), filename)

class Volume(models.Model):
    volume_number = models.PositiveIntegerField(blank=False, null=False)
    series = models.ForeignKey(Series, blank=False, null=False, on_delete=models.CASCADE)
    volume_cover = models.ImageField(blank=True, upload_to=path_file_name)

    class Meta:
        unique_together = ('volume_number', 'series',)


class Chapter(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    chapter_number = models.FloatField(blank=False, null=False)
    folder = models.CharField(max_length=255, blank=True, null=True)
    volume = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    uploaded_on = models.DateTimeField(default=None, blank=True, null=True)

    def clean_chapter_number(self):
        return str(int(self.chapter_number)) if self.chapter_number % 1 == 0 else str(self.chapter_number)

    def slug_chapter_number(self):
        return self.clean_chapter_number().replace(".", "-")



    def __str__(self):
        return f"{self.chapter_number} - {self.title} | {self.group}"

    class Meta:
        ordering = ('chapter_number',)
        unique_together = ('chapter_number', 'series', 'group',)
