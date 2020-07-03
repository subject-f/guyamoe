import json
from ..source import ProxySource
from ..source.data import SeriesAPI, SeriesPage, ChapterAPI
from ..source.helpers import get_wrapper, api_cache
from django.urls import re_path
from django.shortcuts import redirect
from datetime import datetime


class MangaDex(ProxySource):
    def get_chapter_api_prefix(self):
        return "md_chapter"

    def get_series_api_prefix(self):
        return "md_series"

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
            return str(float(resp["chapter"])), str(float(resp["chapter"]))
        except ValueError:
            return "Oneshot", f"0.0{str(resp['timestamp'])}"

    @api_cache(prefix="md_series_dt", time=600)
    def series_api_handler(self, meta_id):
        resp = get_wrapper(f"https://mangadex.org/api/?id={meta_id}&type=manga")
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            groups_dict = {}
            chapters_dict = {}
            for chapter in api_data["chapter"]:
                groups_dict[api_data["chapter"][chapter]["group_id"]] = api_data[
                    "chapter"
                ][chapter]["group_name"]
                if api_data["chapter"][chapter]["lang_code"] == "gb":
                    if api_data["chapter"][chapter]["chapter"] in chapters_dict:
                        if not chapters_dict[api_data["chapter"][chapter]["chapter"]][
                            "volume"
                        ]:
                            chapters_dict[api_data["chapter"][chapter]["chapter"]][
                                "volume"
                            ] = api_data["chapter"][chapter]["volume"]
                        if not chapters_dict[api_data["chapter"][chapter]["chapter"]][
                            "title"
                        ]:
                            chapters_dict[api_data["chapter"][chapter]["chapter"]][
                                "title"
                            ] = api_data["chapter"][chapter]["title"]
                        chapters_dict[api_data["chapter"][chapter]["chapter"]][
                            "groups"
                        ][
                            api_data["chapter"][chapter]["group_id"]
                        ] = self.wrap_chapter_meta(
                            chapter
                        )
                    else:
                        chapters_dict[self.handle_oneshot_chapters(api_data["chapter"][chapter])[1]] = {
                            "volume": api_data["chapter"][chapter]["volume"],
                            "title": api_data["chapter"][chapter]["title"],
                            "groups": {
                                api_data["chapter"][chapter][
                                    "group_id"
                                ]: self.wrap_chapter_meta(chapter)
                            },
                        }
            for chapter in chapters_dict:
                if not chapters_dict[chapter]["volume"]:
                    chapters_dict[chapter]["volume"] = "Uncategorized"
            return SeriesAPI(
                slug=meta_id,
                title=api_data["manga"]["title"],
                description=api_data["manga"]["description"],
                author=api_data["manga"]["author"],
                artist=api_data["manga"]["artist"],
                groups=groups_dict,
                cover="https://mangadex.org" + api_data["manga"]["cover_url"],
                chapters=chapters_dict,
            )
        else:
            return None

    @api_cache(prefix="md_chapter_dt", time=3600)
    def chapter_api_handler(self, meta_id):
        resp = get_wrapper(
            f"https://mangadex.org/api/?id={meta_id}&saver=1&type=chapter",
            headers={"Referer": "https://mangadex.org"},
        )
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            chapter_pages = [
                f"{api_data['server']}{api_data['hash']}/{page}"
                for page in api_data["page_array"]
            ]
            return ChapterAPI(
                pages=chapter_pages,
                series=api_data["manga_id"],
                chapter=self.handle_oneshot_chapters(api_data)[1],
            )
        else:
            return None

    @api_cache(prefix="md_series_page_dt", time=600)
    def series_page_handler(self, meta_id):
        resp = get_wrapper(
            f"https://mangadex.org/api/?id={meta_id}&type=manga",
            headers={"Referer": "https://mangadex.org"},
        )
        if resp.status_code == 200:
            data = resp.text
            api_data = json.loads(data)
            print(api_data)
            chapter_list = []
            latest_chap_id = next(iter(api_data["chapter"]))
            date = datetime.utcfromtimestamp(
                api_data["chapter"][latest_chap_id]["timestamp"]
            )
            last_updated = (
                api_data["chapter"][latest_chap_id]["chapter"],
                datetime.utcfromtimestamp(
                    api_data["chapter"][latest_chap_id]["timestamp"]
                ).strftime("%Y-%m-%d"),
            )
            chapter_dict = {}
            for ch in api_data["chapter"]:
                if api_data["chapter"][ch]["lang_code"] == "gb":
                    chapter_list_id, chapter_id = self.handle_oneshot_chapters(api_data["chapter"][ch])
                    date = datetime.utcfromtimestamp(
                        api_data["chapter"][ch]["timestamp"]
                    )
                    if api_data["chapter"][ch]["chapter"] in chapter_dict:
                        chapter_dict[chapter_id] = [
                            chapter_list_id,
                            chapter_id,
                            api_data["chapter"][ch]["title"],
                            chapter_id.replace(".", "-"),
                            "Multiple Groups",
                            [
                                date.year,
                                date.month - 1,
                                date.day,
                                date.hour,
                                date.minute,
                                date.second,
                            ],
                            api_data["chapter"][ch]["volume"],
                        ]
                    else:
                        chapter_dict[chapter_id] = [
                            chapter_list_id,
                            chapter_id,
                            api_data["chapter"][ch]["title"],
                            chapter_id.replace(".", "-"),
                            api_data["chapter"][ch]["group_name"],
                            [
                                date.year,
                                date.month - 1,
                                date.day,
                                date.hour,
                                date.minute,
                                date.second,
                            ],
                            api_data["chapter"][ch]["volume"],
                        ]
            chapter_list = [
                x[1]
                for x in sorted(
                    chapter_dict.items(), key=lambda m: float(m[0]), reverse=True
                )
            ]
            return SeriesPage(
                series=api_data["manga"]["title"],
                alt_titles=[],
                alt_titles_str=None,
                slug=meta_id,
                cover_vol_url="https://mangadex.org" + api_data["manga"]["cover_url"],
                metadata=[
                    ["Author", api_data["manga"]["author"]],
                    ["Artist", api_data["manga"]["artist"]],
                    ["Last Updated", f"Ch. {last_updated[0]} - {last_updated[1]}"],
                ],
                synopsis=api_data["manga"]["description"],
                author=api_data["manga"]["author"],
                chapter_list=chapter_list,
                original_url=f"https://mangadex.org/title/{meta_id}",
            )
        else:
            return None
