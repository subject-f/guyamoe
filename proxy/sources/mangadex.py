from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import ChapterAPI, SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper

SUPPORTED_LANGS = ["gb"]


class MangaDex(ProxySource):
    def get_reader_prefix(self):
        return "mangadex"

    def shortcut_instantiator(self):
        def series(request, series_id):
            return redirect(f"reader-{self.get_reader_prefix()}-series-page", series_id)

        def series_chapter(request, series_id, chapter, page="1"):
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page",
                series_id,
                chapter,
                page,
            )

        def chapter(request, chapter_id, page="1"):
            data = self.chapter_api_handler(chapter_id)
            if data:
                data = data.objectify()
                return redirect(
                    f"reader-{self.get_reader_prefix()}-chapter-page",
                    str(data["series"]),
                    str(data["chapter"]),
                    page,
                )
            else:
                return HttpResponse(status=500)

        return [
            re_path(r"^title/(?P<series_id>[\d]{1,9})/$", series),
            re_path(r"^title/(?P<series_id>[\d]{1,9})/([\w-]+)/$", series),
            re_path(r"^manga/(?P<series_id>[\d]{1,9})/$", series),
            re_path(r"^manga/(?P<series_id>[\d]{1,9})/([\w-]+)/$", series),
            re_path(r"^chapter/(?P<chapter_id>[\d]{1,9})/$", chapter),
            re_path(
                r"^chapter/(?P<chapter_id>[\d]{1,9})/(?P<page>[\d]{1,9})/$", chapter
            ),
            re_path(r"^(?:read|reader)/md_proxy/(?P<series_id>[\d]+)/$", series),
            re_path(
                r"^(?:read|reader)/md_proxy/(?P<series_id>[\d]+)/(?P<chapter>[\d]+)/$",
                series_chapter,
            ),
            re_path(
                r"^(?:read|reader)/md_proxy/(?P<series_id>[\d]+)/(?P<chapter>[\d]+)/(?P<page>[\d]+)/$$",
                series_chapter,
            ),
        ]

    def handle_oneshot_chapters(self, resp):
        """This expects a chapter API response object."""
        try:
            parse = (
                (lambda s: str(float(s)))
                if "." in resp["chapter"]
                else (lambda s: str(int(s)))
            )
            return parse(resp["chapter"]), parse(resp["chapter"])
        except ValueError:
            return "Oneshot", f"0.0{str(resp['timestamp'])}"

    @api_cache(prefix="md_series_dt", time=180)
    def series_api_handler(self, meta_id):
        resp = get_wrapper(
            f"https://api.mangadex.org/v2/manga/{meta_id}?include=chapters",
            headers={"Referer": "https://mangadex.org"},
        )
        if resp.status_code == 200:
            api_data = resp.json()["data"]
            groups_dict = {
                str(group["id"]): group["name"] for group in api_data["groups"]
            }
            chapters_dict = {}
            for chapter in api_data["chapters"]:
                if chapter["language"] in SUPPORTED_LANGS:
                    if chapter["chapter"] in chapters_dict:
                        current_chapter = chapters_dict[chapter["chapter"]]
                        if (
                            not current_chapter["volume"]
                            or current_chapter["volume"] == "Uncategorized"
                        ):
                            current_chapter["volume"] = (
                                chapter["volume"] or "Uncategorized"
                            )
                        if not current_chapter["title"]:
                            current_chapter["title"] = chapter["title"]
                        current_chapter["groups"][
                            chapter["groups"][0]
                        ] = self.wrap_chapter_meta(chapter["id"])
                    else:
                        chapters_dict[self.handle_oneshot_chapters(chapter)[1]] = {
                            "volume": chapter["volume"] or "Uncategorized",
                            "title": chapter["title"],
                            "groups": {
                                chapter["groups"][0]: self.wrap_chapter_meta(
                                    chapter["id"]
                                )
                            },
                        }

            return SeriesAPI(
                slug=meta_id,
                title=api_data["manga"]["title"],
                description=api_data["manga"]["description"],
                author=api_data["manga"]["author"],
                artist=api_data["manga"]["artist"],
                groups=groups_dict,
                cover=api_data["manga"]["mainCover"],
                chapters=chapters_dict,
            )
        else:
            return None

    @api_cache(prefix="md_chapter_dt", time=180)
    def chapter_api_handler(self, meta_id):
        resp = get_wrapper(
            f"https://api.mangadex.org/v2/chapter/{meta_id}",
            headers={"Referer": "https://mangadex.org"},
        )
        if resp.status_code == 200:
            api_data = resp.json()["data"]
            chapter_pages = [
                f"{api_data['server']}{api_data['hash']}/{page}"
                for page in api_data["pages"]
            ]
            return ChapterAPI(
                pages=chapter_pages,
                series=api_data["mangaId"],
                chapter=self.handle_oneshot_chapters(api_data)[1],
            )
        else:
            return None

    @api_cache(prefix="md_series_page_dt", time=180)
    def series_page_handler(self, meta_id):
        resp = get_wrapper(
            f"https://api.mangadex.org/v2/manga/{meta_id}?include=chapters",
            headers={"Referer": "https://mangadex.org"},
        )
        if resp.status_code == 200:
            api_data = resp.json()["data"]
            groups = {group["id"]: group["name"] for group in api_data["groups"]}
            latest_chapter = 0
            latest_timestamp = 0
            chapters_dict = {}
            for chapter in api_data["chapters"]:
                if chapter["language"] in SUPPORTED_LANGS:
                    chapter_list_id, chapter_id = self.handle_oneshot_chapters(chapter)
                    date = datetime.utcfromtimestamp(chapter["timestamp"])
                    if chapter["timestamp"] > latest_timestamp:
                        latest_chapter = chapter["chapter"]
                        latest_timestamp = chapter["timestamp"]
                    if chapter["chapter"] in chapters_dict:
                        chapters_dict[chapter_id][4] = "Multiple Groups"
                        if not chapters_dict[chapter_id][6]:
                            chapters_dict[chapter_id][6] = chapter["volume"]
                    else:
                        chapters_dict[chapter_id] = [
                            chapter_list_id,
                            chapter_id,
                            chapter["title"],
                            chapter_id.replace(".", "-"),
                            groups[chapter["groups"][0]],
                            [
                                date.year,
                                date.month - 1,
                                date.day,
                                date.hour,
                                date.minute,
                                date.second,
                            ],
                            chapter["volume"],
                        ]
            chapter_list = [
                x[1]
                for x in sorted(
                    chapters_dict.items(), key=lambda m: float(m[0]), reverse=True
                )
            ]
            latest_timestamp = datetime.utcfromtimestamp(latest_timestamp).strftime(
                "%Y-%m-%d"
            )
            return SeriesPage(
                series=api_data["manga"]["title"],
                alt_titles=[],
                alt_titles_str=None,
                slug=meta_id,
                cover_vol_url=api_data["manga"]["mainCover"],
                metadata=[
                    ["Author", api_data["manga"]["author"][0]],
                    ["Artist", api_data["manga"]["artist"][0]],
                    ["Last Updated", f"Ch. {latest_chapter} - {latest_timestamp}"],
                ],
                synopsis=api_data["manga"]["description"],
                author=api_data["manga"]["author"][0],
                chapter_list=chapter_list,
                original_url=f"https://mangadex.org/title/{meta_id}",
            )
        else:
            return None
