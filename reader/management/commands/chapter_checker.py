from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from reader.models import Group, Series, Volume, Chapter
from api.views import random_chars, clear_pages_cache, create_preview_pages

from datetime import datetime, timezone
import pyppeteer as pp
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import re
import os
import io
import zipfile
import traceback

class Command(BaseCommand):
    help = 'Import new chapters from JaiminisBox and Mangadex'

    def add_arguments(self, parser):
        # # Positional arguments
        parser.add_argument('--lookup', nargs='?', default='all')
        parser.add_argument('--dl_md', nargs='?')

        # # Named (optional) arguments
        # parser.add_argument(
        #     '--jb',
        #     action='store_true',
        #     help='lookup specific site. options: jb or md',
        # )
        # parser.add_argument(
        #     '--jb',
        #     action='store_true',
        #     help='lookup specific site. options: jb or md',
        # )
    

    def __init__(self):
        self.browser = None
        self.page = None
        self.jaiminisbox_manga = {
            "Kaguya-Wants-To-Be-Confessed-To": "https://jaiminisbox.com/reader/series/kaguya-wants-to-be-confessed-to/",
            "We-Want-To-Talk-About-Kaguya": "https://jaiminisbox.com/reader/series/we-want-to-talk-about-kaguya/",
            "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": "https://jaiminisbox.com/reader/series/kaguya-wants-to-be-confessed-to-official-doujin/"
        }
        self.mangadex_manga = {
            "We-Want-To-Talk-About-Kaguya": "https://mangadex.org/title/29338/we-want-to-talk-about-kaguya"
        }
        self.jb_group = 3
        self.md_group = 2


    async def get_pages(self, chapter):
        try:
            browser = await pp.launch()
            chapter["pages"] = []
            p = 1
            while True:
                try:
                    self.page = await browser.newPage()
                    await self.page.goto(chapter["url"] + f"/{p}")
                    image_dom = await self.page.waitForSelector("img.noselect", timeout=6000)
                    image_url = await self.page.evaluate("(image_dom) => image_dom.src", image_dom)
                    is_end = re.search(r'(\d+)\.\w+$', image_url).group(1)
                    if is_end == "1" and p != 1:
                        break
                    if p == 1:
                        chapter["title"] = await self.page.querySelectorEval(".chapter-title", "(title) => title.textContent")
                        total_pages = await self.page.querySelectorEval(".reader-controls-page-text > .total-pages", "(totalPages) => totalPages.textContent")
                        chapter["total_pages"] = int(total_pages)
                    chapter["pages"].append(image_url)
                    await self.page.close()
                    p += 1
                except pp.errors.TimeoutError:
                    if p == chapter["total_pages"] + 1:
                        print("Finished indexing all pages for this chapter.")
                    else:
                        traceback.print_exc()
                    break
        except:
            traceback.print_exc()
            chapter = {}
            return chapter
        finally:
            await browser.close()
            return chapter

    def create_chapter_obj(self, chapter, group, series, latest_volume, chapter_data):
        chapter_number = float(chapter)
        chapter_folder_numb = f"{int(chapter_number):04}"
        chapter_folder_numb += f"-{str(chapter_number).rsplit('.')[1]}_" if not str(chapter_number).endswith("0") else "_"
        uid = chapter_folder_numb + random_chars()
        Chapter.objects.create(chapter_number=chapter_number, group=group, series=series, folder=uid, title=chapter_data["title"], volume=latest_volume, uploaded_on=datetime.utcnow().replace(tzinfo=timezone.utc))
        chapter_folder = os.path.join(settings.MEDIA_ROOT, "manga", series.slug, "chapters", uid)
        os.makedirs(os.path.join(chapter_folder, str(group.id)))
        os.makedirs(os.path.join(chapter_folder, f"{str(group.id)}_shrunk"))
        os.makedirs(os.path.join(chapter_folder, f"{str(group.id)}_shrunk_blur"))
        clear_pages_cache()
        return chapter_folder, str(group.id)

    async def mangadex_download(self, chapters, series, group, latest_volume, url=""):
        for chapter in chapters:
            chapter_data = await self.get_pages(chapters[chapter])
            if not chapter_data:
                print('could not download chapter')
                continue
            chapter_folder, group_folder = self.create_chapter_obj(chapter, group, series, latest_volume, chapters[chapter])
            padding = len(str(len(chapter_data["pages"])))
            print(f"Downloading chapter {chapter}...")
            async with aiohttp.ClientSession() as session:
                for idx, page in enumerate(chapter_data["pages"]):
                    extension = page.rsplit(".", 1)[1]
                    page_file = f"{str(idx+1).zfill(padding)}.{extension}"
                    async with session.get(page) as resp:
                        if resp.status == 200:
                            page_content = await resp.read()
                            with open(os.path.join(chapter_folder, group_folder, page_file), 'wb') as f:
                                f.write(page_content)
                            create_preview_pages(chapter_folder, group_folder, page_file)

            print(f"Successfully downloaded chapter and added to db.")

    async def mangadex_checker(self, downloaded_chapters, series, latest_volume, url):
        chapters = {}
        group = Group.objects.get(pk=self.md_group)
        series = Series.objects.get(slug=series)
        self.browser = await pp.launch()
        self.page = await self.browser.newPage()
        try:
            await self.page.goto(url)
            try:
                elements = await self.page.waitForSelector(".page-link", timeout=8000)
                total_pages = int(elements[-1].attrs["href"].rsplit("/", 2)[1])
            except pp.errors.TimeoutError:
                total_pages = 1
            for page_numb in range(1, total_pages+1):
                url = f"{url}/chapters/{page_numb}/"
                await self.page.goto(url)
                elements = await self.page.querySelectorAll(".chapter-row")
                for element in elements:
                    release_lang = await element.querySelectorEval(".order-lg-4 span", "(span) => span.title")
                    if release_lang == "English":
                        chapter_text = await element.querySelectorEval(".col-lg-5 a", "(chapter) => chapter.textContent")
                        chapter_regex = re.search(r'Ch. (\d*\.?\d*) - (.*)', chapter_text)
                        if not chapter_regex:
                            continue
                        chap_numb = chapter_regex.group(1)
                        if str(float(chap_numb)) in downloaded_chapters:
                            continue
                        print(f"Found new chapter ({chap_numb}) on MangaDex for {series}.")
                        chapter_url = await element.querySelectorEval(".col-lg-5 a", "(chapter) => chapter.href")
                        chapters[chap_numb] = {"title": chapter_regex.group(2), "url": chapter_url}

            # Get all pages from newly detected chapters
            await self.browser.close()
            await self.mangadex_download(chapters, series, group, latest_volume)
        except:
            traceback.print_exc()
        finally:
            await self.browser.close()

    async def jaiminis_box_checker(self, downloaded_chapters, series, latest_volume, url):
        chapters = {}
        group = Group.objects.get(pk=self.jb_group)
        series = Series.objects.get(slug=series)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    webpage = await resp.text()
                    soup = BeautifulSoup(webpage, "html.parser")
                    for chapter in soup.select(".list .group .element"):
                        chapter_regex = re.search(r'^Chapter (\d*\.?\d*): (.*)$', chapter.select(".title")[0].text)
                        chap_numb = chapter_regex.group(1)
                        if str(float(chap_numb)) in downloaded_chapters:
                            continue
                        else:
                            print(f"Found new chapter ({chap_numb}) on Jaiminisbox for {series}.")
                            chapter_dl_url = chapter.select(".icon_wrapper a")[0]["href"]
                            chapters[chap_numb] = {"title": chapter_regex.group(2), "url": chapter_dl_url}
                else:
                    print(f"Failed to reach JB page for {series}. Response status: {resp.status}")
            for chapter in chapters:
                chapter_folder, group_folder = self.create_chapter_obj(chapter, group, series, latest_volume, chapters[chapter])
                print(f"Downloading chapter {chapter}...")
                async with session.get(chapters[chapter]["url"]) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        with zipfile.ZipFile(io.BytesIO(data)) as zip_file:
                            all_pages = sorted(zip_file.namelist())
                            padding = len(str(len(all_pages)))
                            for idx, page in enumerate(all_pages):
                                extension = page.rsplit(".", 1)[1]
                                page_file = f"{str(idx+1).zfill(padding)}.{extension}"
                                with open(os.path.join(chapter_folder, group_folder, page_file), "wb") as f:
                                    f.write(zip_file.read(page))
                                create_preview_pages(chapter_folder, group_folder, page_file)
                        print(f"Successfully downloaded chapter and added to db.")

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        print(options)
        if options['lookup'] == 'all' or options['lookup'] == 'jb':
            for manga in self.jaiminisbox_manga:
                latest_volume = Volume.objects.filter(series__slug=manga).order_by('-volume_number')[0].volume_number
                chapters = set([str(chapter.chapter_number) for chapter in Chapter.objects.filter(series__slug=manga, group=self.jb_group)])
                # loop.run_until_complete(self.jaiminis_box_checker(chapters, manga, latest_volume, self.jaiminisbox_manga[manga]))
        if options['lookup'] == 'all' or options['lookup'] == 'md':
            for manga in self.mangadex_manga:
                latest_volume = Volume.objects.filter(series__slug=manga).order_by('-volume_number')[0].volume_number
                chapters = set([str(chapter.chapter_number) for chapter in Chapter.objects.filter(series__slug=manga, group=self.md_group)])
                loop.run_until_complete(self.mangadex_checker(chapters, manga, latest_volume, self.mangadex_manga[manga]))
        
        if options['dl_md']:
            for manga in self.mangadex_manga:
                latest_volume = Volume.objects.filter(series__slug=manga).order_by('-volume_number')[0].volume_number
                chapters = set([str(chapter.chapter_number) for chapter in Chapter.objects.filter(series__slug=manga, group=self.md_group)])
                loop.run_until_complete(self.mangadex_download({}, manga, self.md_group, latest_volume, url=options["dl_md"]))
