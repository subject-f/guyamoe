from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from reader.models import Group, Series, Volume, Chapter
from api.views import random_chars, clear_pages_cache

from datetime import datetime, timezone
import pyppeteer as pp
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import re
import os
import io
import shutil
from PIL import ImageFilter, Image
import zipfile
import traceback

class Command(BaseCommand):
    help = 'Create shrunk and blurred versions of chapter pages'

    def create_preview_pages(self, chapter_folder, group_folder, page_file):
        shrunk = Image.open(os.path.join(chapter_folder, group_folder, page_file))
        blur = Image.open(os.path.join(chapter_folder, group_folder, page_file))
        shrunk = shrunk.convert("RGB")
        blur = blur.convert("RGB")
        shrunk.thumbnail((shrunk.width, 250), Image.ANTIALIAS)
        blur.thumbnail((blur.width/8, blur.height/8), Image.ANTIALIAS)
        shrunk.save(os.path.join(chapter_folder, f"{group_folder}_shrunk", page_file), "JPEG", quality=100, optimize=True, progressive=True)
        blur = blur.filter(ImageFilter.GaussianBlur(radius=2))
        blur.save(os.path.join(chapter_folder, f"{group_folder}_shrunk_blur", page_file), "JPEG", quality=100, optimize=True, progressive=True)

    def handle(self, *args, **options):
        for manga in os.listdir(os.path.join(settings.MEDIA_ROOT, "manga")):
            for chapter in os.listdir(os.path.join(settings.MEDIA_ROOT, "manga", manga, "chapters")):
                chapter_folder =os.path.join(settings.MEDIA_ROOT,  "manga", manga, "chapters", chapter)
                print(chapter_folder)
                for group_folder in os.listdir(chapter_folder):
                    if "shrunk" in group_folder:
                        shutil.rmtree(f"media/manga/{manga}/chapters/{chapter}/{group_folder}")
                        continue
                    shrunk_folder = os.path.join(chapter_folder, f"{group_folder}_shrunk")
                    blur_folder = os.path.join(chapter_folder, f"{group_folder}_shrunk_blur")
                    if not os.path.exists(shrunk_folder):
                        os.makedirs(shrunk_folder)
                    if not os.path.exists(blur_folder):
                        os.makedirs(blur_folder)
                    for page in os.listdir(os.path.join(chapter_folder, group_folder)):
                        self.create_preview_pages(chapter_folder, group_folder, page)
                        

