from .sources.mangadex import MangaDex
from .sources.nhentai import NHentai
from .sources.foolslide import FoolSlide
from .sources.readmanhwa import ReadManhwa
from .sources.imgur import Imgur
from .sources.mangabox import MangaBox

sources = [MangaDex(), NHentai(), FoolSlide(), ReadManhwa(), Imgur(), MangaBox()]
