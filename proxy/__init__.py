from .sources.foolslide import FoolSlide
from .sources.imgur import Imgur
from .sources.mangabox import MangaBox
from .sources.mangadex import MangaDex
from .sources.nhentai import NHentai
from .sources.readmanhwa import ReadManhwa
from .sources.hitomi import Hitomi
from .sources.gist import Gist

sources = [
    MangaDex(),
    NHentai(),
    FoolSlide(),
    ReadManhwa(),
    Imgur(),
    MangaBox(),
    Hitomi(),
    Gist(),
]
