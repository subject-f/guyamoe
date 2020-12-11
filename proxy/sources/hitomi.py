import json
import re
from datetime import datetime

from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import ChapterAPI, SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper


class Hitomi(ProxySource):
    def get_chapter_api_prefix(self):
        return "ht_chapter"

    def get_series_api_prefix(self):
        return "ht_series"

    def get_reader_prefix(self):
        return "hitomi"

    def shortcut_instantiator(self):
        def handler(request, raw_url):
            series_id = self.extract_hitomi_id(raw_url)
            if "/reader/" in raw_url:
                return redirect(
                    f"reader-{self.get_reader_prefix()}-chapter-page",
                    series_id,
                    "1",
                    "1",  # TODO: parse page
                )
            else:
                return redirect(
                    f"reader-{self.get_reader_prefix()}-series-page", series_id,
                )

        return [
            re_path(r"^ht/(?P<raw_url>[\w\d\/:.-]+)", handler),
        ]

    @staticmethod
    def extract_hitomi_id(url: str):
        return url.split("/")[-1].split("-")[-1].split(".")[-2]

    @staticmethod
    def get_gallery_subdomain(segment: str, base: str):
        number_of_frontends = 3
        g = int(segment, 16)
        if g < 0x30:
            number_of_frontends = 2
        if g < 0x09:
            g = 1
        return chr(97 + g % number_of_frontends) + base

    @staticmethod
    def get_page_from_obj(gallery_id, obj: dict):
        hsh = obj["hash"]
        hash_path_1 = hsh[-1]
        hash_path_2 = hsh[-3:-1]
        ext = "webp" if obj["haswebp"] else obj["name"].split(".")[-1]
        path = "webp" if obj["haswebp"] else "images"
        base = "a" if obj["haswebp"] else "b"

        return f"https://{Hitomi.get_gallery_subdomain(hash_path_2, base)}.hitomi.la/{path}/{hash_path_1}/{hash_path_2}/{hsh}.{ext}"

    @staticmethod
    def wrap_image_url(url):
        return (
            f"https://img-referrer-tunnel.herokuapp.com/{url}?host=https://hitomi.la/"
        )

    def ht_api_common(self, meta_id):
        ht_series_api = f"https://ltn.hitomi.la/galleries/{meta_id}.js"
        resp = get_wrapper(ht_series_api)
        if resp.status_code == 200:
            data = resp.text.replace("var galleryinfo = ", "")
            api_data = json.loads(data)

            title = api_data["title"]

            pages_list = [
                self.wrap_image_url(self.get_page_from_obj(meta_id, page))
                for page in api_data["files"]
            ]
            chapter_dict = {
                "1": {"volume": "1", "title": title, "groups": {"1": pages_list}}
            }
            date = datetime.strptime(f"{api_data['date']}00", "%Y-%m-%d %H:%M:%S%z")
            chapter_list = [
                [
                    "1",
                    "1",
                    title,
                    "1",
                    "hitomi.la",
                    [
                        date.year,
                        date.month - 1,
                        date.day,
                        date.hour,
                        date.minute,
                        date.second,
                    ],
                    "1",
                ]
            ]

            return {
                "slug": meta_id,
                "title": api_data["title"],
                "description": " - ".join(
                    [d["tag"] for d in (api_data.get("tags", []) or [])]
                ),
                "group": "",
                "artist": "",
                "author": "",
                "groups": {"1": "hitomi.la"},
                "series": api_data["title"],
                "alt_titles_str": None,
                "cover": pages_list[0],
                "metadata": [
                    ["Type", api_data.get("type", "Unknown")],
                    ["Language", api_data.get("language", "Unknown")],
                ],
                "chapter_dict": chapter_dict,
                "chapter_list": chapter_list,
                "pages": pages_list,
            }
        else:
            return None

    @api_cache(prefix="ht_series_dt", time=600)
    def series_api_handler(self, meta_id):
        data = self.ht_api_common(meta_id)
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

    @api_cache(prefix="ht_chapter_dt", time=3600)
    def chapter_api_handler(self, meta_id):
        data = self.ht_api_common(meta_id)
        if data:
            return ChapterAPI(pages=data["pages"], series=data["slug"], chapter="1",)
        else:
            return None

    @api_cache(prefix="ht_series_page_dt", time=600)
    def series_page_handler(self, meta_id):
        data = self.ht_api_common(meta_id)
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
                original_url=f"https://ltn.hitomi.la/galleries/{data['slug']}.js",
            )
        else:
            return None
