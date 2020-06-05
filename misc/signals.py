from misc.models import Page, Static
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
import shutil
import os


@receiver(post_delete, sender=Page)
def delete_page(sender, instance, **kwargs):
    folder_path = os.path.join(settings.MEDIA_ROOT, "pages", instance.page_url)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


@receiver(post_delete, sender=Static)
def delete_static_file(sender, instance, **kwargs):
    if instance.static_file and os.path.isfile(instance.static_file.path):
        os.remove(instance.static_file.path)
