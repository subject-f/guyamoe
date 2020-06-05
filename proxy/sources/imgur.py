import json
from ..source import ProxySource
from ..source.data import SeriesAPI, SeriesPage, ChapterAPI
from ..source.helpers import get_wrapper, api_cache
from django.urls import re_path
from django.shortcuts import redirect
from datetime import datetime
from django.conf import settings


class Imgur(ProxySource):
    def get_chapter_api_prefix(self):
        return ""

    def get_series_api_prefix(self):
        return "imgur_album"

    def get_reader_prefix(self):
        return "imgur"

    def shortcut_instantiator(self):
        def handler(request, album_hash):
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page", album_hash, "1", "1",
            )

        return [
            re_path(r"^(?:a|gallery)/(?P<album_hash>[\d\w]+)/$", handler),
        ]

    @api_cache(prefix="imgur_series_dt", time=3600 * 6)
    def series_api_handler(self, meta_id):
        resp = get_wrapper(
            f"https://api.imgur.com/3/album/{meta_id}",
            headers={"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"},
        )
        if resp.status_code == 200:
            api_data = json.loads(resp.text)
            title = api_data["data"]["title"] or ""
            description = api_data["data"]["description"] or ""
            author = api_data["data"]["account_id"] or ""
            artist = ""
            groups = {"1": "imgur"}
            cover = api_data["data"]["images"][0]["link"]
            chapters = {
                "1": {
                    "volume": "1",
                    "title": title,
                    "groups": {
                        "1": [
                            {
                                "description": obj["description"] or "",
                                "src": obj["link"],
                            }
                            for obj in api_data["data"]["images"]
                        ]
                    },
                }
            }
            return SeriesAPI(
                slug=meta_id,
                title=title,
                description=description,
                author=author,
                artist=artist,
                groups=groups,
                cover=cover,
                chapters=chapters,
            )
        else:
            return None

    def chapter_api_handler(self, meta_id):
        pass

    @api_cache(prefix="imgur_series_page_dt", time=3600 * 6)
    def series_page_handler(self, meta_id):
        resp = get_wrapper(
            f"https://api.imgur.com/3/album/{meta_id}",
            headers={"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"},
        )
        if resp.status_code == 200:
            api_data = json.loads(resp.text)
            title = api_data["data"]["title"] or ""
            description = api_data["data"]["description"] or ""
            author = api_data["data"]["account_id"] or ""
            cover = api_data["data"]["images"][0]["link"]
            date = datetime.utcfromtimestamp(api_data["data"]["datetime"])
            return SeriesPage(
                series=title,
                alt_titles=[],
                alt_titles_str=None,
                slug=meta_id,
                cover_vol_url=cover,
                metadata=[],
                synopsis=description,
                author=author,
                chapter_list=[
                    [
                        "1",
                        "1",
                        title,
                        "1",
                        author or "imgur",
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
                ],
                original_url=api_data["data"]["link"],
            )
        else:
            return None
