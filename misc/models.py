from django.db import models
import os

# Create your models here.
class Variable(models.Model):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=300)

    def __str__(self):
        return self.key


def path_file_name(instance, filename):
    return os.path.join("pages", instance.page.page_url, "static/", filename)


class Page(models.Model):
    content = models.TextField(blank=True, null=True)
    standalone = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    page_title = models.CharField(max_length=300, blank=False, null=False, unique=True)
    page_url = models.CharField(max_length=300, blank=False, null=False, unique=True)
    cover_image_url = models.CharField(max_length=512, blank=True, null=True)
    date = models.DateTimeField(default=None, blank=True, null=True, db_index=True)
    variable = models.ManyToManyField(Variable, blank=True)

    def __str__(self):
        return self.page_title

    def get_absolute_url(self):
        return f"/pages/{self.page_url}/"


class Static(models.Model):
    static_file = models.FileField(upload_to=path_file_name)
    page = models.ForeignKey(Page, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.static_file)
