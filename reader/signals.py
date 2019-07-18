from reader.models import HitCount, Series, Chapter, Volume
from django.db.models.signals import post_delete, post_save
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.conf import settings
from api.views import clear_pages_cache
import shutil
import os


@receiver(post_delete, sender=Series)
def delete_chapter_folder(sender, instance, **kwargs):
    series = ContentType.objects.get(app_label='reader', model='series')
    hit_count_obj = HitCount.objects.filter(content_type=series, object_id=instance.id).first()
    if hit_count_obj:
        hit_count_obj.delete()

@receiver(post_delete, sender=Chapter)
def delete_chapter_folder(sender, instance, **kwargs):
    if instance.folder and instance.series:
        clear_pages_cache()
        folder_path = os.path.join(settings.MEDIA_ROOT, "manga", instance.series.slug, "chapters", instance.folder)
        if os.path.exists(os.path.join(folder_path, str(instance.group.id))):
            shutil.rmtree(os.path.join(folder_path, str(instance.group.id)))
        if os.path.exists(os.path.join(folder_path, f"{str(instance.group.id)}_shrunk")):
            shutil.rmtree(os.path.join(folder_path, f"{str(instance.group.id)}_shrunk"))
        if os.path.exists(os.path.join(folder_path, f"{str(instance.group.id)}_shrunk_blur")):
            shutil.rmtree(os.path.join(folder_path, f"{str(instance.group.id)}_shrunk_blur"))
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            shutil.rmtree(folder_path)
        chapter = ContentType.objects.get(app_label='reader', model='chapter')
        hit_count_obj = HitCount.objects.filter(content_type=chapter, object_id=instance.id).first()
        if hit_count_obj:
            hit_count_obj.delete()

@receiver(post_delete, sender=Volume)
def delete_volume_folder(sender, instance, **kwargs):
    if instance.volume_cover:
        clear_pages_cache()
        folder_path = os.path.join(settings.MEDIA_ROOT, "manga", instance.series.slug, "volume_covers", str(instance.volume_number))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

@receiver(post_save, sender=Chapter)
def save_chapter(sender, instance, **kwargs):
    if instance.series:
        clear_pages_cache()

@receiver(post_save, sender=Volume)
def save_volume(sender, instance, **kwargs):
    if instance.series:
        clear_pages_cache()
