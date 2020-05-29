import requests
import json
from ..source import ProxySource
from ..source.data import SeriesAPI, SeriesPage, ChapterAPI
from ..source.helpers import naive_encode, naive_decode, get_wrapper, api_cache
from django.urls import re_path
from django.shortcuts import redirect
from datetime import datetime
from concurrent import futures


class ReadManhwa(ProxySource):
    def get_chapter_api_prefix(self):
        return "readmanhwa_chapter"

    def get_series_api_prefix(self):
        return "readmanhwa_series"

    def get_reader_prefix(self):
        return "readmanhwa"

    def shortcut_instantiator(self):
        def chapter_handler(request, series_slug, chapter_slug, page=None):
            if page:
                data = self.series_api_handler(series_slug)
                if data:
                    data = data.objectify()
                    search_str = naive_encode(f"{series_slug}/{chapter_slug}")
                    chapter = [
                        ch
                        for ch in data["chapters"]
                        if search_str in data["chapters"][ch]["groups"]["1"]
                    ][0]
                    return redirect(
                        f"reader-{self.get_reader_prefix()}-chapter-page",
                        data["slug"],
                        chapter,
                        page,
                    )
            else:
                return chapter_handler(request, series_slug, chapter_slug, "1")

        def series_handler(request, series_slug):
            return redirect(
                f"reader-{self.get_reader_prefix()}-series-page", series_slug
            )

        return [
            re_path(r"^en/webtoon/(?P<series_slug>[\d\w-]+)/$", series_handler),
            re_path(
                r"^en/webtoon/(?P<series_slug>[\d\w-]+)/(?P<chapter_slug>[\d\w-]+)/$",
                chapter_handler,
            ),
            re_path(
                r"^en/webtoon/(?P<series_slug>[\d\w-]+)/(?P<chapter_slug>[\d\w-]+)/reader/$",
                chapter_handler,
            ),
            re_path(
                r"^en/webtoon/(?P<series_slug>[\d\w-]+)/(?P<chapter_slug>[\d\w-]+)/reader/(?P<page>[\d]+)/$",
                chapter_handler,
            ),
        ]

    @api_cache(prefix="readmanhwa_series_dt", time=600)
    def series_api_handler(self, meta_id):
        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.map(
                lambda req: {"type": req["type"], "res": get_wrapper(req["url"])},
                [
                    {
                        "type": "main",
                        "url": f"https://readmanhwa.com/api/comics/{meta_id}",
                    },
                    {
                        "type": "chapters",
                        "url": f"https://readmanhwa.com/api/comics/{meta_id}/chapters",
                    },
                ],
            )
        slug = None
        title = None
        description = None
        author = None
        artist = None
        groups = {"1": "Readmanhwa"}
        cover = None
        chapters = {}

        for res in result:
            resp = res["res"]
            if resp.status_code == 200:
                api_data = json.loads(resp.text)
                if res["type"] == "main":
                    slug = api_data["slug"]
                    title = api_data["title"]
                    description = api_data["description"]
                    author = (
                        "authors" in api_data
                        and api_data["authors"]
                        and api_data["authors"][0]["name"]
                    ) or ""
                    artist = (
                        "artists" in api_data
                        and api_data["artists"]
                        and api_data["artists"][0]["name"]
                    ) or ""
                    cover = api_data["image_url"]
                elif res["type"] == "chapters":
                    for chapter, data in zip(
                        range(1, len(api_data) + 1), reversed(api_data)
                    ):
                        chapters[str(chapter)] = {
                            "volume": "1",
                            "title": data["name"],
                            "groups": {
                                "1": self.wrap_chapter_meta(
                                    naive_encode(f"{meta_id}/{data['slug']}")
                                )
                            },
                        }
            else:
                return None
        return SeriesAPI(
            slug=slug,
            title=title,
            description=description,
            author=author,
            artist=artist,
            groups=groups,
            cover=cover,
            chapters=chapters,
        )

    @api_cache(prefix="readmanhwa_chapter_dt", time=3600)
    def chapter_api_handler(self, meta_id):
        resp = get_wrapper(
            f"https://readmanhwa.com/api/comics/{naive_decode(meta_id)}/images"
        )
        if resp.status_code == 200:
            api_data = json.loads(resp.text)
            series, chapter = naive_decode(meta_id).split("/")
            return ChapterAPI(
                pages=[page["source_url"] for page in api_data["images"]],
                series=series,
                chapter=chapter,
            )
        else:
            return None

    @api_cache(prefix="readmanhwa_series_page_dt", time=600)
    def series_page_handler(self, meta_id):
        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            result = executor.map(
                lambda req: {"type": req["type"], "res": get_wrapper(req["url"])},
                [
                    {
                        "type": "main",
                        "url": f"https://readmanhwa.com/api/comics/{meta_id}",
                    },
                    {
                        "type": "chapters",
                        "url": f"https://readmanhwa.com/api/comics/{meta_id}/chapters",
                    },
                ],
            )
        series = None
        alt_titles = []
        alt_titles_str = None
        slug = meta_id
        cover_vol_url = None
        metadata = None
        synopsis = None
        author = None
        chapter_list = []
        original_url = None

        for res in result:
            resp = res["res"]
            if resp.status_code == 200:
                api_data = json.loads(resp.text)
                if res["type"] == "main":
                    series = api_data["title"]
                    alt_titles = (
                        [api_data["alternative_title"]]
                        if "alternative_title" in api_data
                        and api_data["alternative_title"]
                        else []
                    )
                    alt_titles_str = (
                        api_data["alternative_title"]
                        if "alternative_title" in api_data
                        and api_data["alternative_title"]
                        else None
                    )
                    cover_vol_url = api_data["image_url"]
                    metadata = [
                        [
                            "Author",
                            (
                                "authors" in api_data
                                and api_data["authors"]
                                and api_data["authors"][0]["name"]
                            )
                            or "Unknown",
                        ],
                        [
                            "Artist",
                            (
                                "artists" in api_data
                                and api_data["artists"]
                                and api_data["artists"][0]["name"]
                            )
                            or "Unknown",
                        ],
                    ]
                    synopsis = api_data["description"]
                    author = (
                        "authors" in api_data
                        and api_data["authors"]
                        and api_data["authors"][0]["name"]
                    ) or "Unknown"
                    original_url = api_data["short_url"]
                elif res["type"] == "chapters":
                    for chapter, data in zip(range(len(api_data), 0, -1), api_data):
                        chapter_list.append(
                            [
                                str(chapter),
                                str(chapter),
                                data["name"],
                                str(chapter),
                                "Readmanhwa",
                                data["added_at"],
                                "1",
                            ]
                        )
            else:
                return None
        return SeriesPage(
            series=series,
            alt_titles=alt_titles,
            alt_titles_str=alt_titles_str,
            slug=slug,
            cover_vol_url=cover_vol_url,
            metadata=metadata,
            synopsis=synopsis,
            author=author,
            chapter_list=chapter_list,
            original_url=original_url,
        )
