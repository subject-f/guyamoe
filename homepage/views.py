from django.shortcuts import render, redirect
from django.utils.decorators import decorator_from_middleware
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_control
from django.core.cache import cache
from django.conf import settings

from reader.middleware import OnlineNowMiddleware
from homepage.middleware import ForwardParametersMiddleware
from reader.models import Volume, Chapter
from reader.views import series_page_data


@staff_member_required
@cache_control(public=True, max_age=30, s_maxage=30)
def admin_home(request):
    online = cache.get("online_now")
    peak_traffic = cache.get("peak_traffic")
    return render(
        request,
        "homepage/admin_home.html",
        {
            "online": len(online),
            "peak_traffic": peak_traffic,
            "template": "home",
            "version_query": settings.STATIC_VERSION,
        },
    )


@cache_control(public=True, max_age=300, s_maxage=300)
@decorator_from_middleware(OnlineNowMiddleware)
def home(request):
    home_screen_series = {
        "Kaguya-Wants-To-Be-Confessed-To": "",
        "We-Want-To-Talk-About-Kaguya": "",
        "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": "",
    }
    for series in home_screen_series:
        if series == "Kaguya-Wants-To-Be-Confessed-To":
            vols = Volume.objects.filter(series__slug=series).order_by("volume_number")
        else:
            vols = Volume.objects.filter(series__slug=series).order_by("-volume_number")
        for vol in vols:
            if vol.volume_cover:
                filename, ext = str(vol.volume_cover).rsplit(".", 1)
                home_screen_series[series] = [
                    f"/media/{vol.volume_cover}",
                    f"/media/{filename}.webp",
                    f"/media/{filename}_blur.{ext}",
                ]
                break
    data = series_page_data("Kaguya-Wants-To-Be-Confessed-To")
    return render(
        request,
        "homepage/home.html",
        {
            "abs_url": request.build_absolute_uri(),
            "main_series_data": data,
            "main_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][0],
            "main_cover_webp": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][1],
            "main_cover_blur": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][2],
            "4koma_cover": home_screen_series["We-Want-To-Talk-About-Kaguya"][0],
            "4koma_cover_webp": home_screen_series["We-Want-To-Talk-About-Kaguya"][1],
            "4koma_cover_blur": home_screen_series["We-Want-To-Talk-About-Kaguya"][2],
            "doujin_cover": home_screen_series[
                "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"
            ][0],
            "doujin_cover_webp": home_screen_series[
                "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"
            ][1],
            "doujin_cover_blur": home_screen_series[
                "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"
            ][2],
            "relative_url": "",
            "template": "home",
            "version_query": settings.STATIC_VERSION,
        },
    )


@cache_control(public=True, max_age=3600, s_maxage=300)
@decorator_from_middleware(OnlineNowMiddleware)
def about(request):
    return render(
        request,
        "homepage/about.html",
        {
            "relative_url": "about/",
            "template": "about",
            "version_query": settings.STATIC_VERSION,
        },
    )


@decorator_from_middleware(ForwardParametersMiddleware)
def main_series_chapter(request, chapter):
    return redirect(
        "reader-manga-chapter", "Kaguya-Wants-To-Be-Confessed-To", chapter, "1"
    )


@decorator_from_middleware(ForwardParametersMiddleware)
def main_series_page(request, chapter, page):
    return redirect(
        "reader-manga-chapter", "Kaguya-Wants-To-Be-Confessed-To", chapter, page
    )


@decorator_from_middleware(ForwardParametersMiddleware)
def latest(request):
    latest_chap = cache.get("latest_chap")
    if not latest_chap:
        latest_chap = (
            Chapter.objects.order_by("-chapter_number")
            .filter(series__slug="Kaguya-Wants-To-Be-Confessed-To")[0]
            .slug_chapter_number()
        )
        cache.set("latest_chap", latest_chap, 3600 * 96)
    return redirect(
        "reader-manga-chapter", "Kaguya-Wants-To-Be-Confessed-To", latest_chap, "1"
    )


# def latest_releases(request):
#     latest_releases = cache.get("latest_releases")
#     if not latest_releases:
#         latest_releases = Chapter.objects.order_by('-uploaded_on')
#         latest_list = []
#         #for _ in range(0, 10):

#         cache.set("latest_chap", latest_chap, 3600 * 96)
#     return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", latest_chap, "1")


def handle404(request, exception):
    return render(request, "homepage/how_cute_404.html", status=404)
