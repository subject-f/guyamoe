from django.db import models

# Create your models here.
class Page(models.Model):
    content = models.TextField(blank=True, null=True)
    page_title = models.CharField(max_length=300, blank=False, null=False, unique=True)
    page_url = models.CharField(max_length=300, blank=False, null=False, unique=True)
    date = models.DateTimeField(default=None, blank=True, null=True, db_index=True)