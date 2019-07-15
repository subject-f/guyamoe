from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from reader.models import Series, Volume, Chapter


def home(request):
    cached_request = cache.get("home_page")
    if not cached_request:
        home_screen_series = {"Kaguya-Wants-To-Be-Confessed-To": "", "We-Want-To-Talk-About-Kaguya": "", "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": ""}
        for series in home_screen_series:
            vols = Volume.objects.filter(series__slug=series).order_by('-volume_number')
            for vol in vols:
                if vol.volume_cover:
                    home_screen_series[series] = f"/media/{vol.volume_cover}"
                    break
        cached_request = {
            "abs_url": request.build_absolute_uri(),
            "main_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"],
            "4koma_cover": home_screen_series["We-Want-To-Talk-About-Kaguya"],
            "doujin_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"]
        }
        cache.set("home_page", cached_request, 3600 * 12)
    return render(request, 'homepage/home.html', cached_request)


@cache_page(3600)
def about(request):
    return render(request, 'homepage/about.html', {})