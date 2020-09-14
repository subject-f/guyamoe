import os
import shutil

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from misc.models import Page, Static


@receiver(post_delete, sender=Page)
def delete_page(sender, instance, **kwargs):
    folder_path = os.path.join(settings.MEDIA_ROOT, "pages", instance.page_url)
    shutil.rmtree(folder_path, ignore_errors=True)


@receiver(post_delete, sender=Static)
def delete_static_file(sender, instance, **kwargs):
    if instance.static_file and os.path.isfile(instance.static_file.path):
        os.remove(instance.static_file.path)
