from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.http import condition
from django.core.cache import cache
from django.conf import settings

from api.api import all_chapter_data_etag, md_chapter_info
from guyamoe.settings import STATIC_VERSION
from reader.middleware import OnlineNowMiddleware
from reader.users_cache_lib import get_user_ip
from homepage.middleware import ForwardParametersMiddleware
from reader.models import Series, Volume, Chapter
from reader.views import series_page_data

import requests

@staff_member_required
def admin_home(request):
    online = cache.get("online_now")
    peak_traffic = cache.get("peak_traffic")
    return render(request, 'homepage/admin_home.html', {"online": len(online), "peak_traffic": peak_traffic, "template": "home", "version_query": STATIC_VERSION})

@cache_control(max_age=60)
@condition(etag_func=all_chapter_data_etag)
@decorator_from_middleware(OnlineNowMiddleware)
def home(request):
    home_screen_series = {"Kaguya-Wants-To-Be-Confessed-To": "", "We-Want-To-Talk-About-Kaguya": "", "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": ""}
    for series in home_screen_series:
        if series == "Kaguya-Wants-To-Be-Confessed-To":
            vols = Volume.objects.filter(series__slug=series).order_by('volume_number')
        else:
            vols = Volume.objects.filter(series__slug=series).order_by('-volume_number')
        for vol in vols:
            if vol.volume_cover:
                filename, ext = str(vol.volume_cover).rsplit('.', 1)
                home_screen_series[series] = [f"/media/{vol.volume_cover}", f"/media/{filename}.webp", f"/media/{filename}_blur.{ext}"]
                break
    data = series_page_data("Kaguya-Wants-To-Be-Confessed-To")
    return render(request, 'homepage/home.html', {
            "abs_url": request.build_absolute_uri(),
            "main_series_data": data,
            "main_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][0],
            "main_cover_webp": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][1],
            "main_cover_blur": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][2],
            "4koma_cover": home_screen_series["We-Want-To-Talk-About-Kaguya"][0],
            "4koma_cover_webp": home_screen_series["We-Want-To-Talk-About-Kaguya"][1],
            "4koma_cover_blur": home_screen_series["We-Want-To-Talk-About-Kaguya"][2],
            "doujin_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"][0],
            "doujin_cover_webp": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"][1],
            "doujin_cover_blur": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"][2],
            "relative_url": "",
            "template": "home",
            "version_query": STATIC_VERSION
        })

@cache_page(3600 * 48)
@decorator_from_middleware(OnlineNowMiddleware)
def about(request):
    return render(request, 'homepage/about.html', {"relative_url": "about/", "template": "about", "version_query": STATIC_VERSION})

@decorator_from_middleware(ForwardParametersMiddleware)
def main_series_chapter(request, chapter):
    return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", chapter, "1")

@decorator_from_middleware(ForwardParametersMiddleware)
def main_series_page(request, chapter, page):
    return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", chapter, page)

@decorator_from_middleware(ForwardParametersMiddleware)
def latest(request):
    latest_chap = cache.get("latest_chap")
    if not latest_chap:
        latest_chap = Chapter.objects.order_by('-chapter_number').filter(series__slug="Kaguya-Wants-To-Be-Confessed-To")[0].slug_chapter_number()
        cache.set("latest_chap", latest_chap, 3600 * 96)
    return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", latest_chap, "1")

@decorator_from_middleware(ForwardParametersMiddleware)
def md_series(request, md_series_id):
    return redirect('reader-md-proxy', md_series_id)

@decorator_from_middleware(ForwardParametersMiddleware)
def md_chapter(request, md_chapter_id, page=1):
    chapter_info = md_chapter_info(md_chapter_id)
    return redirect('reader-md-chapter', chapter_info["series_id"], str(chapter_info["chapter"]).replace(".", "-"), page)

@decorator_from_middleware(ForwardParametersMiddleware)
def nh_series(request, nh_series_id, page=None):
    if page:
        return redirect('reader-nh-chapter', nh_series_id, 1, page)
    else:
        return redirect('reader-nh-proxy', nh_series_id)

def referral(request):
    if request.method == "POST":
        ip = get_user_ip(request)
        referral_metadata = cache.get(f"referral_{ip}")
        if referral_metadata and not referral_metadata["consumed"]:
            if request.POST["rid"] == referral_metadata["rid"]:
                cache.set(f"referral_{ip}", {"consumed": True}, 1800)
                try:
                    requests.post(settings.REFERRAL_SERVICE, referral_metadata)
                except:
                    pass
        return HttpResponse(status=200)
    else:
        return handle404(request, "")

# def latest_releases(request):
#     latest_releases = cache.get("latest_releases")
#     if not latest_releases:
#         latest_releases = Chapter.objects.order_by('-uploaded_on')
#         latest_list = []
#         #for _ in range(0, 10):

#         cache.set("latest_chap", latest_chap, 3600 * 96)
#     return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", latest_chap, "1")

def handle404(request, exception):
    return render(request, 'homepage/how_cute_404.html', status=404)
