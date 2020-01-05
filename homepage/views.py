from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from reader.models import Series, Volume, Chapter


@staff_member_required
def admin_home(request):
    return render(request, 'homepage/admin_home.html')


@cache_page(3600 * 48)
def home(request):
    home_screen_series = {"Kaguya-Wants-To-Be-Confessed-To": "", "We-Want-To-Talk-About-Kaguya": "", "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": ""}
    for series in home_screen_series:
        vols = Volume.objects.filter(series__slug=series).order_by('-volume_number')
        for vol in vols:
            if vol.volume_cover:
                filename, ext = str(vol.volume_cover).rsplit('.', 1)
                home_screen_series[series] = [f"/media/{vol.volume_cover}", f"/media/{filename}.webp", f"/media/{filename}_blur.{ext}"]
                break
    return render(request, 'homepage/home.html', {
            "abs_url": request.build_absolute_uri(),
            "main_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][0],
            "main_cover_webp": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][1],
            "main_cover_blur": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"][2],
            "4koma_cover": home_screen_series["We-Want-To-Talk-About-Kaguya"][0],
            "4koma_cover_webp": home_screen_series["We-Want-To-Talk-About-Kaguya"][1],
            "4koma_cover_blur": home_screen_series["We-Want-To-Talk-About-Kaguya"][2],
            "doujin_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"][0],
            "doujin_cover_webp": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"][1],
            "doujin_cover_blur": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"][2],
            "relative_url": ""
        })

@cache_page(3600 * 48)
def about(request):
    return render(request, 'homepage/about.html', {"relative_url": "about/"})


def main_series_chapter(request, chapter):
    return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", chapter, "1")

def main_series_page(request, chapter, page):
    return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", chapter, page)

def latest(request):
    latest_chap = cache.get("latest_chap")
    if not latest_chap:
        latest_chap = Chapter.objects.order_by('-chapter_number').filter(series__slug="Kaguya-Wants-To-Be-Confessed-To")[0].slug_chapter_number()
        cache.set("latest_chap", latest_chap, 3600 * 96)
    return redirect('reader-manga-chapter', "Kaguya-Wants-To-Be-Confessed-To", latest_chap, "1")

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
