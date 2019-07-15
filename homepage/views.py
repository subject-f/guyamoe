from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from reader.models import Series, Volume, Chapter


@cache_page(3600)
def home(request):
    home_screen_series = {"Kaguya-Wants-To-Be-Confessed-To": "", "We-Want-To-Talk-About-Kaguya": "", "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin": ""}
    for series in home_screen_series:
        vols = Volume.objects.filter(series__slug=series).order_by('-volume_number')
        for vol in vols:
            if vol.volume_cover:
                home_screen_series[series] = f"/media/{vol.volume_cover}"
                break
    return render(request, 'homepage/home.html', {
        "abs_url": request.build_absolute_uri(),
        "main_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To"],
        "4koma_cover": home_screen_series["We-Want-To-Talk-About-Kaguya"],
        "doujin_cover": home_screen_series["Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"]
    })


@cache_page(3600)
def about(request):
    return render(request, 'homepage/about.html', {})