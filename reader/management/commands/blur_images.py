import asyncio
import io
import os
import re
import shutil
import traceback
import zipfile
from datetime import datetime, timezone

import aiohttp
import pyppeteer as pp
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageFilter

from api.api import chapter_post_process, clear_pages_cache, random_chars
from reader.models import Chapter, Group, Series, Volume


class Command(BaseCommand):
    help = "Create shrunk and blurred versions of chapter pages"

    def handle(self, *args, **options):
        for chapter in Chapter.objects.all():
            chapter_post_process(chapter, update_version=False)
