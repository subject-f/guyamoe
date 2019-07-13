from reader.models import Chapter, Volume
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
import shutil
import os

@receiver(post_delete, sender=Chapter)
def delete_chapter_folder(sender, instance, **kwargs):
    if instance.folder and instance.series:
        folder_path = os.path.join(settings.MEDIA_ROOT, "manga", instance.series.slug, "chapters", instance.folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

@receiver(post_delete, sender=Volume)
def delete_volume_folder(sender, instance, **kwargs):
    if instance.volume_cover:
        folder_path = os.path.join(settings.MEDIA_ROOT, "manga", instance.series.slug, "volume_covers", str(instance.volume_number))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)