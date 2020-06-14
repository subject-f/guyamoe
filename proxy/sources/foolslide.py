import json
import re
import base64
from ..source import ProxySource
from ..source.data import SeriesAPI, SeriesPage, ChapterAPI
from ..source.helpers import (
    naive_encode,
    naive_decode,
    post_wrapper,
    get_wrapper,
    api_cache,
)
from django.urls import re_path
from django.shortcuts import redirect
from datetime import datetime
from bs4 import BeautifulSoup
import requests


class FoolSlide(ProxySource):
    def get_chapter_api_prefix(self):
        return "fs_chapter"

    def get_series_api_prefix(self):
        return "fs_series"

    def get_reader_prefix(self):
        return "foolslide"

    def shortcut_instantiator(self):
        def handler(request, raw_url):
            if raw_url.endswith("/"):
                raw_url = raw_url[:-1]
            if "/read/" in raw_url:
                params = [n for n in raw_url.split("/") if n]
                # ~~Translator~~ Developer's note: "en" means only english FS sites work
                lang_idx = params.index("en")
                chapter = params[lang_idx + 2]
                if len(params) - 1 > lang_idx + 2 and params[lang_idx + 3] != "page":
                    chapter += f"-{params[lang_idx + 3]}"
                page = "1"
                if "/page/" in raw_url:
                    page_idx = params.index("page")
                    page = params[page_idx + 1]
                return redirect(
                    f"reader-{self.get_reader_prefix()}-chapter-page",
                    self.encode_slug(raw_url),
                    chapter,
                    page,
                )
            elif "/series/" in raw_url:
                return redirect(
                    f"reader-{self.get_reader_prefix()}-series-page",
                    self.encode_slug(raw_url),
                )
            else:
                return HttpResponse(status=400)

        def series(request, series_id):
            # A hacky bandaid that shouldn't be here, but it'll otherwise redirect since we're
            # masking the canonnical route and it'll keep matching the regex path
            if "%" in series_id:
                series_id = self.encode_slug(naive_decode(series_id))
            return redirect(f"reader-{self.get_reader_prefix()}-series-page", series_id)

        def series_chapter(request, series_id, chapter, page="1"):
            if "%" in series_id:
                series_id = self.encode_slug(naive_decode(series_id))
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page",
                series_id,
                chapter,
                page,
            )

        return [
            re_path(r"^fs/(?P<raw_url>[\w\d\/:.-]+)", handler),
            re_path(r"^(?:read|reader)/fs_proxy/(?P<series_id>[\w\d.%-]+)/$", series),
            re_path(
                r"^(?:read|reader)/fs_proxy/(?P<series_id>[\w\d.%-]+)/(?P<chapter>[\d]+)/$",
                series_chapter,
            ),
            re_path(
                r"^(?:read|reader)/fs_proxy/(?P<series_id>[\w\d.%-]+)/(?P<chapter>[\d]+)/(?P<page>[\d]+)/$",
                series_chapter,
            ),
            re_path(
                r"^proxy/foolslide/(?P<series_id>[\w\d.%-]+)/$",
                series,
            ),
            re_path(
                r"^proxy/foolslide/(?P<series_id>[\w\d.%-]+)/(?P<chapter>[\d-]+)/(?P<page>[\d]+)/$",
                series_chapter,
            )
        ]

    def encode_slug(self, url):
        url = (
            url.replace("/read/", "/series/")
            .replace("https://", "")
            .replace("http://", "")
        )
        split = url.split("/")
        url = "/".join(split[0 : split.index("series") + 2])
        return self.encode(url)

    @staticmethod
    def decode(url: str):
        return str(base64.urlsafe_b64decode(url.encode()), "utf-8")

    @staticmethod
    def encode(url: str):
        return str(base64.urlsafe_b64encode(url.encode()), "utf-8")

    def fs_scrape_common(self, meta_id):
        try:
            resp = post_wrapper(
                f"https://{self.decode(meta_id)}/", data={"adult": "true"}
            )
        except requests.exceptions.ConnectionError:
            resp = post_wrapper(
                f"http://{self.decode(meta_id)}/", data={"adult": "true"}
            )
        if resp.status_code == 200:
            data = resp.text
            soup = BeautifulSoup(data, "html.parser")

            comic_info = soup.find("div", class_="large comic")

            title = (
                comic_info.find("h1", class_="title")
                .get_text()
                .replace("\n", "")
                .strip()
            )
            description = comic_info.find("div", class_="info").get_text().strip()
            groups_dict = {"1": self.decode(meta_id).split("/")[0]}
            cover_div = soup.find("div", class_="thumbnail")
            if cover_div and cover_div.find("img")["src"]:
                cover = cover_div.find("img")["src"]
            else:
                cover = ""

            chapter_dict = {}
            chapter_list = []

            for a in soup.find_all("div", class_="element"):
                link = a.find("div", class_="title").find("a")
                chapter_regex = re.search(r"(Chapter |Ch.)([\d.]+)", link.get_text())
                chapter_number = "0"
                if chapter_regex:
                    chapter_number = chapter_regex.group(2)
                volume_regex = re.search(r"(Volume |Vol.)([\d.]+)", link.get_text())
                volume_number = "1"
                if volume_regex:
                    volume_number = volume_regex.group(2)

                chapter = {
                    "volume": volume_number,
                    "title": link.get_text(),
                    "groups": {"1": None},
                }
                chp = chapter_number.split(".")
                major_chapter = chp[0]
                minor_chapter = "0"
                if len(chp) > 1:
                    minor_chapter = chp[1]
                deconstructed_url = link["href"].split("/read/")
                chapter_url = self.wrap_chapter_meta(
                    self.encode(
                        f"{deconstructed_url[0]}/api/reader/chapter?comic_stub={deconstructed_url[1].split('/')[0]}&chapter={major_chapter}&subchapter={minor_chapter}"
                    )
                )
                chapter["groups"]["1"] = chapter_url
                chapter_dict[chapter_number] = chapter

                chapter_title = link.get_text()
                upload_info = list(
                    map(
                        lambda e: e.strip(),
                        a.find("div", class_="meta_r")
                        .get_text()
                        .replace("by", "")
                        .split(","),
                    )
                )
                chapter_list.append(
                    [
                        chapter_number,
                        chapter_number,
                        chapter_title,
                        chapter_number.replace(".", "-"),
                        upload_info[0],
                        upload_info[1],
                        "",
                    ]
                )

            return {
                "slug": meta_id,
                "title": title,
                "description": description,
                "series": title,
                "alt_titles_str": None,
                "cover_vol_url": cover,
                "metadata": [],
                "author": "",
                "artist": "",
                "groups": groups_dict,
                "cover": cover,
                "chapter_dict": chapter_dict,
                "chapter_list": chapter_list,
            }
        else:
            return None

    @api_cache(prefix="fs_series_dt", time=600)
    def series_api_handler(self, meta_id):
        data = self.fs_scrape_common(meta_id)
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

    @api_cache(prefix="fs_chapter_dt", time=3600)
    def chapter_api_handler(self, meta_id):
        resp = get_wrapper(self.decode(meta_id))
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return ChapterAPI(
                pages=[e["url"] for e in data["pages"]], series=meta_id, chapter=""
            )
        else:
            return None

    @api_cache(prefix="fs_series_page_dt", time=600)
    def series_page_handler(self, meta_id):
        data = self.fs_scrape_common(meta_id)
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
                original_url=f"https://{self.decode(meta_id)}/",
            )
        else:
            return None
