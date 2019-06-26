from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'homepage/home.html', {})


def about(request):
    return render(request, 'homepage/about.html', {})