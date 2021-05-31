import os
import shutil
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save, pre_save, post_init
from django.dispatch import receiver
from PIL import Image, ImageFilter

from api.api import clear_pages_cache, delete_chapter_pages_if_exists
from reader.models import Chapter, HitCount, Series, Volume, new_volume_folder


@receiver(post_delete, sender=Series)
def delete_series_hitcount(sender, instance, **kwargs):
    series = ContentType.objects.get(app_label="reader", model="series")
    hit_count_obj = HitCount.objects.filter(
        content_type=series, object_id=instance.id
    ).first()
    if hit_count_obj:
        hit_count_obj.delete()


@receiver(post_delete, sender=Chapter)
def delete_chapter_folder(sender, instance, **kwargs):
    if instance.folder and instance.series:
        clear_pages_cache()
        folder_path = os.path.join(
            settings.MEDIA_ROOT,
            "manga",
            instance.series.slug,
            "chapters",
            instance.folder,
        )
        delete_chapter_pages_if_exists(
            folder_path, instance.clean_chapter_number(), str(instance.group.id)
        )
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)
        chapter = ContentType.objects.get(app_label="reader", model="chapter")
        hit_count_obj = HitCount.objects.filter(
            content_type=chapter, object_id=instance.id
        ).first()
        if hit_count_obj:
            hit_count_obj.delete()
        clear_pages_cache()


@receiver(post_delete, sender=Volume)
def delete_volume_folder(sender, instance, **kwargs):
    if instance.volume_cover:
        clear_pages_cache()
        folder_path = os.path.join(
            settings.MEDIA_ROOT,
            "manga",
            instance.series.slug,
            "volume_covers",
            str(instance.volume_number),
        )
        shutil.rmtree(folder_path, ignore_errors=True)


@receiver(pre_save, sender=Chapter)
def pre_save_chapter(sender, instance, **kwargs):
    if instance.reprocess_metadata:
        instance.reprocess_metadata = False
        instance.save()
        chapter_post_process(instance, is_update=False)

    if instance.series and instance.series.next_release_page:
        highest_chapter_number = Chapter.objects.filter(series=instance.series).latest(
            "chapter_number"
        )
        if instance.chapter_number > highest_chapter_number.chapter_number:
            instance.series.next_release_time = datetime.utcnow().replace(
                tzinfo=timezone.utc
            ) + timedelta(days=7)
            instance.series.save()

@receiver(post_init, sender=Chapter)
def remember_original_series_of_chapter(sender, instance, **kwargs):
    instance.old_chapter_number = str(instance.slug_chapter_number()) if instance.chapter_number is not None else None
    instance.old_series_slug = str(instance.series.slug) if hasattr(instance, 'series') else None
    instance.old_group_id = str(instance.group.id) if hasattr(instance, 'group') else None


@receiver(post_save, sender=Chapter)
def post_save_chapter(sender, instance, **kwargs):
    # If the group or series or the chapter number has changed, move all chapter file
    if (instance.old_series_slug is not None and str(instance.series.slug) != instance.old_series_slug) or \
       (instance.old_group_id is not None and str(instance.group.id) != instance.old_group_id) or \
       (instance.old_chapter_number is not None and str(instance.slug_chapter_number()) != instance.old_chapter_number):

        new_group_id = str(instance.group.id)

        old_chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", instance.old_series_slug, "chapters", instance.folder, instance.old_group_id)
        new_chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", instance.series.slug, "chapters", instance.folder, new_group_id)

        os.makedirs(os.path.dirname(new_chapter_folder), exist_ok=True)
        if old_chapter_folder != new_chapter_folder or str(instance.slug_chapter_number()) != instance.old_chapter_number:
            shutil.move(f"{old_chapter_folder}_{instance.old_chapter_number}.zip", f"{new_chapter_folder}_{instance.slug_chapter_number()}.zip")

        if old_chapter_folder != new_chapter_folder:
            shutil.move(old_chapter_folder, new_chapter_folder)
            shutil.move(f"{old_chapter_folder}_shrunk", f"{new_chapter_folder}_shrunk")
            shutil.move(f"{old_chapter_folder}_shrunk_blur", f"{new_chapter_folder}_shrunk_blur")

    if instance.series:
        clear_pages_cache()


@receiver(post_init, sender=Volume)
def remember_original_series_of_volume(sender, instance, **kwargs):
    instance.old_series_slug = str(instance.series.slug) if hasattr(instance, 'series') else None
    instance.old_volume_number = int(instance.volume_number) if instance.volume_number else None
    instance.old_volume_cover = None if instance.volume_cover is None else str(instance.volume_cover)

@receiver(post_save, sender=Volume)
def save_volume(sender, instance, **kwargs):
    if instance.series:
        clear_pages_cache()
    if instance.volume_cover is None or instance.volume_cover == "":
        return
    # If series has been changed or the volume has been changed, move images
    # and a cover has been set in the past and a new cover has not been uploaded
    if instance.old_series_slug is not None and (instance.old_series_slug != str(instance.series.slug) or instance.old_volume_number != int(instance.volume_number)) \
        and instance.old_volume_cover is not None and instance.old_volume_cover == instance.volume_cover:
        old_location = os.path.join(settings.MEDIA_ROOT, os.path.dirname(str(instance.old_volume_cover)))
        new_location = os.path.join(settings.MEDIA_ROOT, new_volume_folder(instance))
        if os.path.normpath(old_location) != os.path.normpath(new_location):
            os.makedirs(new_location, exist_ok=True)
            for file in os.listdir(old_location):
                os.rename(os.path.join(old_location, file), os.path.join(new_location, file))
            os.rmdir(old_location)
            original_filename = os.path.basename(str(instance.volume_cover))
            instance.volume_cover = os.path.join(new_volume_folder(instance), original_filename)

            # setup it up to prevent a recursive loop of save call back
            instance.old_series_slug = str(instance.series.slug)
            instance.old_volume_number = int(instance.volume_number)
            instance.old_volume_cover = str(instance.volume_cover)
            instance.save()
    elif instance.volume_cover and (instance.old_volume_cover is None or instance.old_volume_cover != instance.volume_cover):
        save_dir = os.path.join(os.path.dirname(str(instance.volume_cover)))
        vol_cover = os.path.basename(str(instance.volume_cover))
        for old_data in os.listdir(os.path.join(settings.MEDIA_ROOT, save_dir)):
            if old_data != vol_cover:
                os.remove(os.path.join(settings.MEDIA_ROOT, save_dir, old_data))
        filename, ext = vol_cover.rsplit(".", 1)
        image = Image.open(os.path.join(settings.MEDIA_ROOT, save_dir, vol_cover))
        image.save(
            os.path.join(settings.MEDIA_ROOT, save_dir, f"{filename}.webp"),
            lossless=False,
            quality=60,
            method=6,
        )
        # This line crash on my server and this file does not seem be used at all.
        # image.save(os.path.join(settings.MEDIA_ROOT, save_dir, f"{filename}.jp2"))
        blur = Image.open(os.path.join(settings.MEDIA_ROOT, save_dir, vol_cover))
        blur = blur.convert("RGB")
        blur.thumbnail((blur.width / 8, blur.height / 8), Image.ANTIALIAS)
        blur = blur.filter(ImageFilter.GaussianBlur(radius=4))
        blur.save(
            os.path.join(settings.MEDIA_ROOT, save_dir, f"{filename}_blur.{ext}"),
            "JPEG",
            quality=100,
            optimize=True,
            progressive=True,
        )
