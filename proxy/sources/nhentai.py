import json
from datetime import datetime

from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import ChapterAPI, SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper


class NHentai(ProxySource):
    def get_reader_prefix(self):
        return "nhentai"

    def shortcut_instantiator(self):
        def handler(request, series_id, page=None):
            if page:
                return redirect(
                    f"reader-{self.get_reader_prefix()}-chapter-page",
                    series_id,
                    "1",
                    page,
                )
            else:
                return redirect(
                    f"reader-{self.get_reader_prefix()}-series-page", series_id
                )

        def series(request, series_id):
            return redirect(f"reader-{self.get_reader_prefix()}-series-page", series_id)

        def series_chapter(request, series_id, chapter, page="1"):
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page",
                series_id,
                chapter,
                page,
            )

        return [
            re_path(r"^g/(?P<series_id>[\d]{1,9})/$", handler),
            re_path(r"^g/(?P<series_id>[\d]{1,9})/(?P<page>[\d]{1,9})/$", handler),
            re_path(r"^(?:read|reader)/nh_proxy/(?P<series_id>[\w\d.%-]+)/$", series),
            re_path(
                r"^(?:read|reader)/nh_proxy/(?P<series_id>[\w\d.%-]+)/(?P<chapter>[\d]+)/$",
                series_chapter,
            ),
            re_path(
                r"^(?:read|reader)/nh_proxy/(?P<series_id>[\w\d.%-]+)/(?P<chapter>[\d]+)/(?P<page>[\d]+)/$$",
                series_chapter,
            ),
        ]

    @api_cache(prefix="nh_series_common_dt", time=3600)
    def nh_api_common(self, meta_id):
        nh_series_api = f"https://nhentai.net/api/gallery/{meta_id}"
        resp = get_wrapper(nh_series_api)
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)

            artist = api_data["scanlator"]
            group = api_data["scanlator"]
            lang_list = []
            tag_list = []
            for tag in api_data["tags"]:
                if tag["type"] == "artist":
                    artist = tag["name"]
                elif tag["type"] == "group":
                    group = tag["name"]
                elif tag["type"] == "language":
                    lang_list.append(tag["name"])
                elif tag["type"] == "tag":
                    tag_list.append(tag["name"])

            pages_list = []
            for p, t in enumerate(api_data["images"]["pages"]):
                file_format = "jpg"
                if t["t"] == "p":
                    file_format = "png"
                if t["t"] == "g":
                    file_format = "gif"
                pages_list.append(
                    f"https://i.nhentai.net/galleries/{api_data['media_id']}/{p + 1}.{file_format}"
                )

            groups_dict = {"1": group or "N-Hentai"}
            chapters_dict = {
                "1": {
                    "volume": "1",
                    "title": api_data["title"]["pretty"]
                    or api_data["title"]["english"],
                    "groups": {"1": pages_list},
                }
            }

            return {
                "slug": meta_id,
                "title": api_data["title"]["pretty"] or api_data["title"]["english"],
                "description": api_data["title"]["english"],
                "group": group,
                "artist": artist,
                "groups": groups_dict,
                "tags": tag_list,
                "lang": ", ".join(lang_list),
                "chapters": chapters_dict,
                "cover": f"https://t.nhentai.net/galleries/{api_data['media_id']}/cover.{'jpg' if api_data['images']['cover']['t'] == 'j' else 'png'}",
                "timestamp": api_data["upload_date"],
            }
        else:
            return None

    @api_cache(prefix="nh_series_dt", time=3600)
    def series_api_handler(self, meta_id):
        data = self.nh_api_common(meta_id)
        if data:
            return SeriesAPI(
                slug=meta_id,
                title=data["title"],
                description=data["description"],
                author=data["artist"],
                artist=data["artist"],
                groups=data["groups"],
                cover=data["cover"],
                chapters=data["chapters"],
            )
        else:
            return None

    @api_cache(prefix="nh_pages_dt", time=3600)
    def chapter_api_handler(self, meta_id):
        data = self.nh_api_common(meta_id)
        if data:
            return ChapterAPI(
                pages=data["chapters"]["1"]["groups"]["1"],
                series=data["slug"],
                chapter="1",
            )
        else:
            return None

    @api_cache(prefix="nh_series_page_dt", time=3600)
    def series_page_handler(self, meta_id):
        data = self.nh_api_common(meta_id)
        if data:
            date = datetime.utcfromtimestamp(data["timestamp"])
            chapter_list = [
                [
                    "1",
                    "1",
                    data["title"],
                    "1",
                    data["group"] or "NHentai",
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
            return SeriesPage(
                series=data["title"],
                alt_titles=[],
                alt_titles_str=None,
                slug=data["slug"],
                cover_vol_url=data["cover"],
                metadata=[["Author", data["artist"]], ["Artist", data["artist"]]],
                synopsis=f"{data['description']}\n\n{' - '.join(data['tags'])}",
                author=data["artist"],
                chapter_list=chapter_list,
                original_url=f"https://nhentai.net/g/{meta_id}/",
            )
        else:
            return None
