from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from reader.models import Group, Series, Volume, Chapter
from api.api import random_chars, clear_pages_cache, chapter_post_process

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

    def handle(self, *args, **options):
        for chapter in Chapter.objects.all():
            chapter_post_process(chapter, update_version=False)
