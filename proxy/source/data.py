class SeriesAPI:
    def __init__(self, **kwargs):
        self.args = kwargs

    def objectify(self):
        return {
            "slug": self.args["slug"],
            "title": self.args["title"],
            "description": self.args["description"],
            "author": self.args["author"],
            "artist": self.args["artist"],
            "groups": self.args["groups"],
            "cover": self.args["cover"],
            "chapters": self.args["chapters"],
            "series_name": self.args["title"],
        }


class SeriesPage:
    def __init__(self, **kwargs):
        self.args = kwargs

    def objectify(self):
        return {
            "series": self.args["series"],
            "alt_titles": self.args["alt_titles"],
            "alt_titles_str": self.args["alt_titles_str"],
            "slug": self.args["slug"],
            "cover_vol_url": self.args["cover_vol_url"],
            "metadata": self.args["metadata"],
            "synopsis": self.args["synopsis"],
            "author": self.args["author"],
            "chapter_list": self.args["chapter_list"],
            "original_url": self.args["original_url"],
            "available_features": ["detailed"],
        }


class ChapterAPI:
    def __init__(self, **kwargs):
        self.args = kwargs

    def objectify(self):
        return {
            "series": self.args["series"],
            "pages": self.args["pages"],
            "chapter": self.args["chapter"],
        }
