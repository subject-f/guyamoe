import json
from datetime import datetime

from django.conf import settings
from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import ChapterAPI, SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper


class Pastebin(ProxySource):
    def get_chapter_api_prefix(self):
        return ""

    def get_series_api_prefix(self):
        return "pastebin"

    def get_reader_prefix(self):
        return "pastebin"

    def shortcut_instantiator(self):
        def handler(request, pastebin_hash):
            return redirect(
                f"reader-{self.get_reader_prefix()}-series-page", pastebin_hash
            )

        return [
            re_path(r"^(?:pb|paste|p|pastebin)/(?P<pastebin_hash>[\d\w]+)/$", handler),
        ]

    @staticmethod
    def get_chapter_url(raw_url):
        # Hardcoded, this is meh
        pass

    @api_cache(prefix="pastebin_common_dt", time=60)
    def pastebin_common(self, meta_id):
        resp = get_wrapper(f"https://pastebin.com/raw/{meta_id}")
        if resp.status_code == 200:
            api_data = json.loads(resp.text)
            title = api_data.get("title", "")
            description = api_data.get("description", "")
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
                    "No date.",
                    ch[1]["volume"],
                ]
                for ch in sorted(
                    chapter_dict.items(), key=lambda m: float(m[0]), reverse=True
                )
            ]

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

    @api_cache(prefix="pastebin_dt", time=3600 * 6)
    def series_api_handler(self, meta_id):
        data = self.pastebin_common(meta_id)
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

    @api_cache(prefix="pastebin_page_dt", time=3600 * 6)
    def series_page_handler(self, meta_id):
        data = self.pastebin_common(meta_id)
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
                original_url=f"https://pastebin.com/{data['slug']}",
            )
        else:
            return None
