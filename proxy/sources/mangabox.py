import json
import re
from ..source import ProxySource
from ..source.data import SeriesAPI, SeriesPage, ChapterAPI
from ..source.helpers import get_wrapper, api_cache, decode, encode
from django.urls import re_path
from django.shortcuts import redirect
from datetime import datetime
from bs4 import BeautifulSoup


class MangaBox(ProxySource):
    def get_chapter_api_prefix(self):
        return "mb_chapter"

    def get_series_api_prefix(self):
        return "mb_series"

    def get_reader_prefix(self):
        return "mangabox"

    def shortcut_instantiator(self):
        def handler(request, raw_url):
            if "/chapter/" in raw_url:
                canonical_chapter = self.parse_chapter(raw_url)
                return redirect(
                    f"reader-{self.get_reader_prefix()}-chapter-page",
                    encode(self.normalize_slug(raw_url)),
                    canonical_chapter,
                    "1",
                )
            else:
                return redirect(
                    f"reader-{self.get_reader_prefix()}-series-page",
                    encode(self.normalize_slug(raw_url)),
                )

        return [
            re_path(r"^mb/(?P<raw_url>[\w\d\/:.-]+)", handler),
        ]

    @staticmethod
    def wrap_image_url(url):
        return f"https://img-referrer-tunnel.herokuapp.com/{url}?host=mangakakalot.com"

    @staticmethod
    def normalize_slug(denormal):
        if "/chapter/" in denormal:
            return "https://" + "/".join(
                [
                    part
                    for part in denormal.replace("/chapter/", "/manga/").split("/")
                    if part
                ][1 if denormal.startswith("http") else 0 : -1]
            )
        else:
            return denormal

    @staticmethod
    def construct_url(raw):
        decoded = decode(raw)
        return ("" if decoded.startswith("http") else "https://") + decoded

    @staticmethod
    def parse_chapter(raw_url):
        return [ch for ch in raw_url.split("/") if ch][-1].replace("chapter_", "")

    def mb_scrape_common(self, meta_id):
        decoded_url = self.construct_url(meta_id)
        resp = get_wrapper(decoded_url)
        # There's a page redirect sometimes
        if resp.status_code == 200 and "window.location.assign" in resp.text:
            decoded_url = re.findall(
                r"(?:window.location.assign\(\")([\s\S]+)(?:\"\))", resp.text
            )
            if decoded_url:
                resp = get_wrapper(decoded_url[0])
            else:
                return None
        if resp.status_code == 200:
            data = resp.text
            soup = BeautifulSoup(data, "html.parser")
            elems = soup.select("div.manga-info-top, div.panel-story-info")
            if not elems:
                return None
            metadata = BeautifulSoup(str(elems), "html.parser")
            try:
                title = metadata.select_one("h1, h2").text
            except AttributeError:
                return None
            try:
                author = (
                    metadata.find(
                        lambda element: element.name == "td"
                        and "author" in element.text.lower()
                    )
                    .findNext("td")
                    .text
                )
            except AttributeError:
                author = "None"
            try:
                description = soup.select_one(
                    "div#noidungm, div#panel-story-info-description"
                ).text.strip()
            except AttributeError:
                description = "No description."
            try:
                cover = metadata.select_one(
                    "div.manga-info-pic img, span.info-image img"
                )["src"]
            except AttributeError:
                cover = ""

            groups_dict = {"1": "MangaBox"}

            chapter_list = []
            chapter_dict = {}
            chapters = list(
                map(
                    lambda a: [
                        a.select_one("a")["title"],
                        a.select_one("a")["href"],
                        a.select("span")[2].text
                        if len(a.select("span")) >= 3
                        else "No date.",
                    ],
                    soup.select("div.chapter-list div.row, ul.row-content-chapter li"),
                )
            )
            for chapter in chapters:
                canonical_chapter = self.parse_chapter(chapter[1])
                chapter_list.append(
                    [
                        "",
                        canonical_chapter,
                        chapter[0],
                        canonical_chapter.replace(".", "-"),
                        "MangaBox",
                        chapter[2],
                        "",
                    ]
                )
                chapter_dict[canonical_chapter] = {
                    "volume": "1",
                    "title": chapter[0],
                    "groups": {"1": self.wrap_chapter_meta(encode(chapter[1]))},
                }

            return {
                "slug": meta_id,
                "title": title,
                "description": description,
                "series": title,
                "alt_titles_str": None,
                "cover_vol_url": cover,
                "metadata": [],
                "author": author,
                "artist": author,
                "groups": groups_dict,
                "cover": cover,
                "chapter_dict": chapter_dict,
                "chapter_list": chapter_list,
            }
        else:
            return None

    @api_cache(prefix="mb_series_dt", time=600)
    def series_api_handler(self, meta_id):
        data = self.mb_scrape_common(meta_id)
        if data:
            return SeriesAPI(
                slug=data["slug"],
                title=data["title"],
                description=data["description"],
                author=data["author"],
                artist=data["artist"],
                groups=data["groups"],
                cover=data["cover"],
                chapters=data["chapter_dict"],
            )
        else:
            return None

    @api_cache(prefix="mb_chapter_dt", time=3600)
    def chapter_api_handler(self, meta_id):
        decoded_url = self.construct_url(meta_id)
        resp = get_wrapper(decoded_url)
        if resp.status_code == 200:
            data = resp.text
            soup = BeautifulSoup(data, "html.parser")
            pages = [
                src
                for src in map(
                    lambda a: self.wrap_image_url(a["src"]),
                    soup.select("div#vungdoc img, div.container-chapter-reader img"),
                )
                if not src.endswith("log")
            ]
            return ChapterAPI(pages=pages, series=meta_id, chapter="")
        else:
            return None

    @api_cache(prefix="mb_series_page_dt", time=600)
    def series_page_handler(self, meta_id):
        data = self.mb_scrape_common(meta_id)
        original_url = decode(meta_id)
        if not original_url.startswith("http"):
            original_url = "https://" + original_url
        if data:
            return SeriesPage(
                series=data["title"],
                alt_titles=[],
                alt_titles_str=None,
                slug=data["slug"],
                cover_vol_url=data["cover"],
                metadata=[],
                synopsis=data["description"],
                author=data["artist"],
                chapter_list=data["chapter_list"],
                original_url=original_url,
            )
        else:
            return None
