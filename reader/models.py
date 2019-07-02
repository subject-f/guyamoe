from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=200)


class Group(models.Model):
    name = models.CharField(max_length=200)


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


class Chapter(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    chapter_number = models.FloatField(unique=True, blank=False, null=False)
    folder = models.CharField(max_length=255, blank=True, null=True)
    page_count = models.PositiveSmallIntegerField()
    volume = models.PositiveSmallIntegerField(blank=True, null=True, default=None)
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.SET_NULL)
    uploaded_on = models.DateTimeField(default=None, blank=True, null=True)

    def clean_chapter_number(self):
        return str(int(self.chapter_number)) if self.chapter_number % 1 == 0 else str(self.chapter_number)

    def slug_chapter_number(self):
        return self.clean_chapter_number().replace(".", "-")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('chapter_number',)
