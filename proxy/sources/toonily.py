from bs4 import BeautifulSoup
from django.conf import settings
from django.http.response import Http404
from django.shortcuts import redirect
from django.urls import re_path

from ..source import ProxySource
from ..source.data import ChapterAPI, SeriesAPI, SeriesPage
from ..source.helpers import api_cache, get_wrapper, encode, decode


class Toonily(ProxySource):
    def get_chapter_api_prefix(self):
        return "ty_chapter"

    def get_series_api_prefix(self):
        return "ty_series"

    def get_reader_prefix(self):
        return "toonily"

    def shortcut_instantiator(self):
        def chapter_handler(request, series_slug, chapter_slug, page=None):
            if page:
                data = self.series_api_handler(series_slug)
                if data:
                    data = data.objectify()
                    search_str = encode(f"{series_slug}/{chapter_slug}")
                    chapter = None
                    for ch in data["chapters"]:
                        if search_str in data["chapters"][ch]["groups"]["1"]:
                            chapter = ch
                            break
                    if chapter:
                        return redirect(
                            f"reader-{self.get_reader_prefix()}-chapter-page",
                            data["slug"],
                            chapter,
                            page,
                        )
                    else:
                        raise Http404("Chapter not found")
            else:
                return chapter_handler(request, series_slug, chapter_slug, "1")

        def series_handler(request, series_slug):
            return redirect(
                f"reader-{self.get_reader_prefix()}-series-page", series_slug
            )

        return [
            re_path(r"^webtoon/(?P<series_slug>[\d\w-]+)/$", series_handler),
            re_path(
                r"^webtoon/(?P<series_slug>[\d\w-]+)/(?P<chapter_slug>[\d\w-]+)/$",
                chapter_handler,
            ),
        ]

    @staticmethod
    def wrap_image_url(url):
        return f"{settings.IMAGE_PROXY_URL}/{url}"

    @api_cache(prefix="toonily_series_common_dt", time=600)
    def ty_api_common(self, meta_id):
        resp = get_wrapper(f"https://toonily.com/webtoon/{meta_id}/")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.select_one(".post-title h1").text
            description = soup.select_one(".summary__content p").text
            author = soup.select_one(".author-content a").text
            artist = soup.select_one(".artist-content a").text
            groups = {"1": "Toonily"}
            cover = soup.select_one(".summary_image img")["data-src"]
            chapter_dict = {}
            chapter_list = []
            chapters = list(
                map(
                    lambda a: [
                        a.select_one("a").text.strip(),
                        a.select_one("a")["href"].split("/")[-2]
                        if a.select_one("a")["href"].endswith("/")
                        else a.select_one("a")["href"].split("/")[-1],
                        a.select_one("span").text,
                    ],
                    reversed(soup.select(".wp-manga-chapter")),
                )
            )
            for i, chapter in enumerate(chapters):
                chapter_dict[str(i)] = {
                    "volume": "1",
                    "title": chapter[0],
                    "groups": {
                        "1": self.wrap_chapter_meta(encode(f"{meta_id}/{chapter[1]}"))
                    },
                }
                chapter_list.append(
                    [
                        "",
                        str(i),
                        chapter[0],
                        str(i),
                        "Toonily",
                        chapter[2],
                        "1",
                    ]
                )
            chapter_list.reverse()
            return {
                "slug": meta_id,
                "title": title,
                "description": description,
                "author": author,
                "artist": artist,
                "groups": groups,
                "chapter_dict": chapter_dict,
                "chapter_list": chapter_list,
                "cover": cover,
            }
        else:
            return None

    @api_cache(prefix="toonily_series_dt", time=600)
    def series_api_handler(self, meta_id):
        data = self.ty_api_common(meta_id)
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

    @api_cache(prefix="toonily_pages_dt", time=600)
    def chapter_api_handler(self, meta_id):
        resp = get_wrapper(f"https://toonily.com/webtoon/{decode(meta_id)}/")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            pages = map(lambda e: e.select_one("img"), soup.select("div.page-break"))
            pages = [
                self.wrap_image_url(elem.get("data-src", elem.get("src")).strip())
                for elem in pages
            ]

            return ChapterAPI(pages=pages, series=meta_id, chapter=meta_id)
        else:
            return None

    @api_cache(prefix="toonily_series_page_dt", time=600)
    def series_page_handler(self, meta_id):
        data = self.ty_api_common(meta_id)
        if data:
            return SeriesPage(
                series=data["title"],
                alt_titles=[],
                alt_titles_str=None,
                slug=data["slug"],
                cover_vol_url=data["cover"],
                metadata=[["Author", data["author"]], ["Artist", data["artist"]]],
                synopsis=data["description"],
                author=data["author"],
                chapter_list=data["chapter_list"],
                original_url=f"https://toonily.com/webtoon/{meta_id}/",
            )
        else:
            return None
