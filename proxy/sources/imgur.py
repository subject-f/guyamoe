import json
import re
import random
from datetime import datetime

from django.conf import settings
from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import ChapterAPI, SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper


class Imgur(ProxySource):
    def get_reader_prefix(self):
        return "imgur"

    def shortcut_instantiator(self):
        def handler(request, album_hash):
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page",
                album_hash,
                "1",
                "1",
            )

        return [
            re_path(r"^(?:a|gallery)/(?P<album_hash>[\d\w]+)/$", handler),
        ]

    @staticmethod
    def image_url_handler(metadata):
        return (
            metadata["link"] + "?_w."
            if metadata.get("width", 0) > metadata.get("height", 0)
            else metadata["link"]
        )

    def imgur_api_common(self, meta_id):
        """Backup handler using the API. It consumes the API key so be wary."""
        resp = get_wrapper(
            f"https://api.imgur.com/3/album/{meta_id}",
            headers={"Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}"},
        )
        if resp.status_code == 200:
            api_data = resp.json()["data"]
            date = datetime.utcfromtimestamp(api_data["datetime"])
            return {
                "slug": meta_id,
                "title": api_data["title"] or "Untitled",
                "description": api_data["description"] or "No description.",
                "author": api_data["account_id"] or "Unknown",
                "artist": api_data["account_id"] or "Unknown",
                "cover": api_data["images"][0]["link"],
                "groups": {"1": "Imgur"},
                "chapter_dict": {
                    "1": {
                        "volume": "1",
                        "title": api_data["title"] or "No title.",
                        "groups": {
                            "1": [
                                {
                                    "description": obj["description"] or "",
                                    "src": self.image_url_handler(obj),
                                }
                                for obj in api_data["images"]
                            ]
                        },
                    }
                },
                "chapter_list": [
                    [
                        "1",
                        "1",
                        api_data["title"] or "Untitled",
                        "1",
                        api_data["account_id"] or "No group",
                        [
                            date.year,
                            date.month - 1,
                            date.day,
                            date.hour,
                            date.minute,
                            date.second,
                        ],
                        "1",
                    ],
                ],
                "pages_list": [
                    self.image_url_handler(obj) for obj in api_data["images"]
                ],
                "original_url": api_data["link"],
            }
        else:
            return None

    def imgur_embed_common(self, meta_id):
        resp = get_wrapper(
            f"https://imgur.com/a/{meta_id}/embed?cache_buster={random.random()}"
        )
        if resp.status_code == 200:
            data = re.search(
                r"(?:album[\s]+?: )([\s\S]+)(?:,[\s]+?images[\s]+?:)", resp.text
            )
            api_data = json.loads(data.group(1))
            try:
                date = datetime.strptime(api_data["datetime"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                date = datetime.now()
            images = api_data["album_images"]["images"]
            for image in images:
                image["link"] = f"https://i.imgur.com/{image['hash']}{image['ext']}"
            return {
                "slug": meta_id,
                "title": api_data["title"] or "Untitled",
                "description": api_data["description"] or "No description.",
                "author": "Unknown",
                "artist": "Unknown",
                "cover": images[0]["link"],
                "groups": {"1": "Imgur"},
                "chapter_dict": {
                    "1": {
                        "volume": "1",
                        "title": api_data["title"] or "No title.",
                        "groups": {
                            "1": [
                                {
                                    "description": obj["description"] or "",
                                    "src": self.image_url_handler(obj),
                                }
                                for obj in images
                            ]
                        },
                    }
                },
                "chapter_list": [
                    [
                        "1",
                        "1",
                        api_data["title"] or "Untitled",
                        "1",
                        "No group",
                        [
                            date.year,
                            date.month - 1,
                            date.day,
                            date.hour,
                            date.minute,
                            date.second,
                        ],
                        "1",
                    ],
                ],
                "pages_list": [self.image_url_handler(obj) for obj in images],
                "original_url": f"https://imgur.com/a/{api_data['id']}",
            }
        else:
            return None

    @api_cache(prefix="imgur_api_dt", time=300)
    def imgur_common(self, meta_id):
        return self.imgur_embed_common(meta_id)

    @api_cache(prefix="imgur_series_dt", time=300)
    def series_api_handler(self, meta_id):
        data = self.imgur_common(meta_id)
        return (
            SeriesAPI(
                slug=data["slug"],
                title=data["title"],
                description=data["description"],
                author=data["author"],
                artist=data["artist"],
                groups=data["groups"],
                cover=data["cover"],
                chapters=data["chapter_dict"],
            )
            if data
            else None
        )

    @api_cache(prefix="imgur_pages_dt", time=300)
    def chapter_api_handler(self, meta_id):
        data = self.imgur_common(meta_id)
        return (
            ChapterAPI(
                pages=data["pages_list"], series=data["slug"], chapter=data["slug"]
            )
            if data
            else None
        )

    @api_cache(prefix="imgur_series_page_dt", time=300)
    def series_page_handler(self, meta_id):
        data = self.imgur_common(meta_id)
        return (
            SeriesPage(
                series=data["title"],
                alt_titles=[],
                alt_titles_str=None,
                slug=data["slug"],
                cover_vol_url=data["cover"],
                metadata=[],
                synopsis=data["description"],
                author=data["author"],
                chapter_list=data["chapter_list"],
                original_url=data["original_url"],
            )
            if data
            else None
        )
