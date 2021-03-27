import abc
import json
from typing import List

from django.conf import settings
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, re_path
from django.views.decorators.cache import cache_control
from django.utils.html import escape

from .data import *
from .helpers import *

def proxy_redirect(request):
    if request.path.endswith("/"):
        request.path = request.path[:-1]
    return HttpResponseRedirect(f"https://cubari.moe{request.path}/#redirect")

class ProxySource(metaclass=abc.ABCMeta):
    # /proxy/:reader_prefix/slug
    @abc.abstractmethod
    def get_reader_prefix(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def shortcut_instantiator(self) -> List[re_path]:
        raise NotImplementedError

    @abc.abstractmethod
    def series_api_handler(self, meta_id: str) -> SeriesAPI:
        raise NotImplementedError

    @abc.abstractmethod
    def chapter_api_handler(self, meta_id: str) -> ChapterAPI:
        raise NotImplementedError

    @abc.abstractmethod
    def series_page_handler(self, meta_id: str) -> SeriesPage:
        raise NotImplementedError

    def wrap_chapter_meta(self, meta_id):
        return f"/proxy/api/{self.get_reader_prefix()}/chapter/{meta_id}/"

    def process_description(self, desc):
        return escape(desc)

    @cache_control(public=True, max_age=60, s_maxage=60)
    def reader_view(self, request, meta_id, chapter, page=None):
        return proxy_redirect(request)
        if page:
            data = self.series_api_handler(meta_id)
            if data:
                data = data.objectify()
                if chapter.replace("-", ".") in data["chapters"]:
                    data["version_query"] = settings.STATIC_VERSION
                    data["relative_url"] = f"proxy/{self.get_reader_prefix()}/{meta_id}"
                    data["api_path"] = f"/proxy/api/{self.get_reader_prefix()}/series/"
                    data["image_proxy_url"] = settings.IMAGE_PROXY_URL
                    data["reader_modifier"] = f"proxy/{self.get_reader_prefix()}"
                    data["chapter_number"] = chapter.replace("-", ".")
                    return render(request, "reader/reader.html", data)
            return render(request, "homepage/thonk_500.html", status=500)
        else:
            return redirect(
                f"reader-{self.get_reader_prefix()}-chapter-page", meta_id, chapter, "1"
            )

    @cache_control(public=True, max_age=60, s_maxage=60)
    def series_view(self, request, meta_id):
        return proxy_redirect(request)
        data = self.series_page_handler(meta_id)
        if data:
            data = data.objectify()
            data["synopsis"] = self.process_description(data["synopsis"])
            data["version_query"] = settings.STATIC_VERSION
            data["relative_url"] = f"proxy/{self.get_reader_prefix()}/{meta_id}"
            data["reader_modifier"] = f"proxy/{self.get_reader_prefix()}"
            return render(request, "reader/series.html", data)
        else:
            return render(request, "homepage/thonk_500.html", status=500)

    @cache_control(public=True, max_age=60, s_maxage=60)
    def series_api_view(self, request, meta_id):
        return proxy_redirect(request)
        data = self.series_api_handler(meta_id)
        if data:
            data = data.objectify()
            data["description"] = self.process_description(data["description"])
            return HttpResponse(json.dumps(data), content_type="application/json")
        else:
            return render(request, "homepage/thonk_500.html", status=500)

    @cache_control(public=True, max_age=60, s_maxage=60)
    def chapter_api_view(self, request, meta_id):
        return proxy_redirect(request)
        data = self.chapter_api_handler(meta_id)

        if data:
            data = data.objectify()
            return HttpResponse(
                json.dumps(data["pages"]), content_type="application/json"
            )
        else:
            return render(request, "homepage/thonk_500.html", status=500)

    def register_api_routes(self):
        """Routes will be under /proxy/api/<route>"""
        return [
            path(
                f"{self.get_reader_prefix()}/series/<str:meta_id>/",
                self.series_api_view,
                name=f"api-{self.get_reader_prefix()}-series-data",
            ),
            path(
                f"{self.get_reader_prefix()}/chapter/<str:meta_id>/",
                self.chapter_api_view,
                name=f"api-{self.get_reader_prefix()}-chapter-data",
            ),
        ]

    def register_shortcut_routes(self):
        return self.shortcut_instantiator()

    def register_frontend_routes(self):
        return [
            path(
                f"{self.get_reader_prefix()}/<str:meta_id>/",
                self.series_view,
                name=f"reader-{self.get_reader_prefix()}-series-page",
            ),
            path(
                f"{self.get_reader_prefix()}/<str:meta_id>/<str:chapter>/",
                self.reader_view,
                name=f"reader-{self.get_reader_prefix()}-chapter",
            ),
            path(
                f"{self.get_reader_prefix()}/<str:meta_id>/<str:chapter>/<str:page>/",
                self.reader_view,
                name=f"reader-{self.get_reader_prefix()}-chapter-page",
            ),
        ]
