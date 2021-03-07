import json
from datetime import datetime
import random

from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper

"""
Expected format of the raw gists should be:
{
    "title": "<required, str>",
    "description": "<required, str>",
    "artist": "<optional, str>",
    "author": "<optional, str>",
    "cover": "<optional, str>",
    "chapters": {
        "1": {
            "title": "<required, str>",
            "volume": "<optional, str>",
            "groups": {
                "<group name>": "<proxy url>",
                OR
                "<group name>": [
                    "<url to page 1>",
                    "<url to page 2>",
                    ...
                ]
            },
            "last_updated": "<optional, unix timestamp>",
        },
        "2": {
            ...
        },
        ...
    }
}
Make sure you pass in the shortened key from git.io.
"""


class Gist(ProxySource):
    def get_reader_prefix(self):
        return "gist"

    def shortcut_instantiator(self):
        def handler(request, gist_hash):
            # While git.io allows vanity URLs with special characters, chances are
            # they won't parse properly by a regular browser. So we don't deal with it
            return redirect(f"reader-{self.get_reader_prefix()}-series-page", gist_hash)

        return [
            re_path(r"^(?:gist|gh)/(?P<gist_hash>[\d\w/]+)/$", handler),
        ]

    @staticmethod
    def date_parser(timestamp):
        timestamp = int(timestamp)
        date = datetime.utcfromtimestamp(timestamp)
        return [
            date.year,
            date.month - 1,
            date.day,
            date.hour,
            date.minute,
            date.second,
        ]

    @api_cache(prefix="gist_common_dt", time=300)
    def gist_common(self, meta_id):
        resp = get_wrapper(f"https://git.io/{meta_id}", allow_redirects=False)
        if resp.status_code != 302 or not resp.headers["location"]:
            return None
        resp = get_wrapper(f"{resp.headers['location']}?{random.random()}")
        if resp.status_code == 200 and resp.headers["content-type"].startswith(
            "text/plain"
        ):
            api_data = json.loads(resp.text)
            title = api_data.get("title")
            description = api_data.get("description")
            if not title or not description:
                return None

            artist = api_data.get("artist", "")
            author = api_data.get("author", "")
            cover = api_data.get("cover", "")

            groups_set = {
                group
                for ch_data in api_data["chapters"].values()
                for group in ch_data["groups"].keys()
            }
            groups_dict = {str(key): value for key, value in enumerate(groups_set)}
            groups_map = {value: str(key) for key, value in enumerate(groups_set)}

            chapter_dict = {
                ch: {
                    "volume": data.get("volume", "Uncategorized"),
                    "title": data.get("title", ""),
                    "groups": {
                        groups_map[group]: metadata
                        for group, metadata in data["groups"].items()
                    },
                    "last_updated": data.get("last_updated", None),
                }
                for ch, data in api_data["chapters"].items()
            }

            chapter_list = [
                [
                    ch[0],
                    ch[0],
                    ch[1]["title"],
                    ch[0].replace(".", "-"),
                    "Multiple Groups"
                    if len(ch[1]["groups"]) > 1
                    else groups_dict[list(ch[1]["groups"].keys())[0]],
                    "No date."
                    if not ch[1]["last_updated"]
                    else self.date_parser(ch[1]["last_updated"]),
                    ch[1]["volume"],
                ]
                for ch in sorted(
                    chapter_dict.items(), key=lambda m: float(m[0]), reverse=True
                )
            ]

            for md in chapter_dict.values():
                del md["last_updated"]

            return {
                "slug": meta_id,
                "title": title,
                "description": description,
                "series": title,
                "cover_vol_url": cover,
                "metadata": [],
                "author": author,
                "artist": artist,
                "groups": groups_dict,
                "cover": cover,
                "chapter_dict": chapter_dict,
                "chapter_list": chapter_list,
            }
        else:
            return None

    @api_cache(prefix="gist_dt", time=300)
    def series_api_handler(self, meta_id):
        data = self.gist_common(meta_id)
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

    def chapter_api_handler(self, meta_id):
        pass

    @api_cache(prefix="gist_page_dt", time=300)
    def series_page_handler(self, meta_id):
        data = self.gist_common(meta_id)
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
                original_url=f"https://git.io/{meta_id}",
            )
        else:
            return None
