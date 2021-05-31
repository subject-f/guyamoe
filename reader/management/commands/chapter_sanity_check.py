from django.core.management.base import BaseCommand

from reader.models import Chapter, Volume
from django.conf import settings

import os

def is_a_not_empty_folder(path):
    if not os.path.exists(path):
        raise RuntimeError(f"'{path}' does not exist")
    if not os.path.isdir(path):
        raise RuntimeError(f"'{path}' is not a dir")
    if len(os.listdir(path)) == 0:
        raise RuntimeError(f"'{path}' is empty.")

class Command(BaseCommand):
    help = "Check that the file for every chapter do exist at the correct location"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for chapter in Chapter.objects.select_related("series", "group"):
            series_folder = os.path.join(settings.MEDIA_ROOT, "manga", chapter.series.slug)
            chapter_folder = os.path.join(series_folder, "chapters", chapter.folder)
            group_folder = str(chapter.group.id)
            is_a_not_empty_folder(series_folder)
            is_a_not_empty_folder(chapter_folder)
            is_a_not_empty_folder(os.path.join(chapter_folder, f"{group_folder}"))
            is_a_not_empty_folder(os.path.join(chapter_folder, f"{group_folder}_shrunk"))
            is_a_not_empty_folder(os.path.join(chapter_folder, f"{group_folder}_shrunk_blur"))
            print(chapter_folder, "is ok.")

        for volume in Volume.objects.select_related("series"):
            series_folder = os.path.join(settings.MEDIA_ROOT, str(volume.volume_cover))

            if not os.path.exists(series_folder):
                raise RuntimeError(f"'{series_folder}' does not exist")

        print("Success!")
