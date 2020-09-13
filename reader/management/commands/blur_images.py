from django.core.management.base import BaseCommand

from api.api import chapter_post_process
from reader.models import Chapter


class Command(BaseCommand):
    help = "Create shrunk and blurred versions of chapter pages"

    def handle(self, *args, **options):
        for chapter in Chapter.objects.all():
            chapter_post_process(chapter, is_update=False)
