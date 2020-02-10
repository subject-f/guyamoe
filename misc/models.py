from django.db import models

# Create your models here.
class Variable(models.Model):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=300)

    def __str__(self):
        return self.key


class Page(models.Model):
    content = models.TextField(blank=True, null=True)
    page_title = models.CharField(max_length=300, blank=False, null=False, unique=True)
    page_url = models.CharField(max_length=300, blank=False, null=False, unique=True)
    cover_image_url = models.CharField(max_length=300, blank=True, null=True)
    date = models.DateTimeField(default=None, blank=True, null=True, db_index=True)
    variable = models.ManyToManyField(Variable, blank=True)

    def __str__(self):
        return self.page_title
