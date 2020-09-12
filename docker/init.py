import json
import os
import random
import subprocess
import time
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFilter

WIDTH = 850
HEIGHT = 1250
PAGES = 18
PROCESSES = 15

MEDIA_BASE = "media"
FIXTURES_PATH = "./reader/fixtures/reader_fixtures.json"


def real_path(path):
    return os.path.join(MEDIA_BASE, path)


def generate_image(path):
    if not os.path.isfile(real_path(path)):
        print("Generating", path)
        width = WIDTH
        height = HEIGHT
        if "shrunk" in path:
            width = 85
            height = 125
        img = Image.new(
            "RGB",
            (width, height),
            color=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
        )
        ImageDraw.Draw(img).text(
            (width / 2, height / 2), path.split("/")[-1], fill=(0, 0, 0)
        )
        if "blur" in path:
            img.filter(ImageFilter.GaussianBlur(radius=10))
        img.save(real_path(path))
        return True


def create_directories(directories):
    for directory in directories:
        os.makedirs(real_path(directory), exist_ok=True)


def load_fixtures(path):
    with open(path, "r") as fixtures:
        raw = fixtures.read()
        data = json.loads(raw)

        series = {}
        for d in data:
            if d["model"] == "reader.series":
                series[d["pk"]] = d["fields"]["slug"]

        directories = []
        volume_covers = []
        chapters = []
        for d in data:
            f = d["fields"]
            if d["model"] == "reader.chapter":
                directories.append(
                    f"manga/{series[f['series']]}/chapters/{f['folder']}/{f['group']}"
                )
                directories.append(
                    f"manga/{series[f['series']]}/chapters/{f['folder']}/{f['group']}_shrunk"
                )
                directories.append(
                    f"manga/{series[f['series']]}/chapters/{f['folder']}/{f['group']}_shrunk_blur"
                )
                for page_num in range(1, PAGES + 1):
                    chapters.append(
                        f"manga/{series[f['series']]}/chapters/{f['folder']}/{f['group']}/{page_num:03}.jpg"
                    )
                    chapters.append(
                        f"manga/{series[f['series']]}/chapters/{f['folder']}/{f['group']}_shrunk/{page_num:03}.jpg"
                    )
                    chapters.append(
                        f"manga/{series[f['series']]}/chapters/{f['folder']}/{f['group']}_shrunk_blur/{page_num:03}.jpg"
                    )

            elif d["model"] == "reader.volume":
                if f["volume_cover"]:
                    directories.append("/".join(f["volume_cover"].split("/")[0:-1]))
                    volume_covers.append(f["volume_cover"])

        return {
            "volume_covers": volume_covers,
            "chapters": chapters,
            "directories": directories,
        }


if __name__ == "__main__":
    fixtures = load_fixtures(FIXTURES_PATH)
    create_directories(fixtures["directories"])
    with Pool(PROCESSES) as p:
        changed = [
            status
            for status in p.map(
                generate_image, fixtures["chapters"] + fixtures["volume_covers"]
            )
            if status
        ]

    os.system("python manage.py makemigrations")
    result = subprocess.check_output("python manage.py migrate", shell=True, text=True)

    if "OK" in result or changed:
        os.system(f"python manage.py loaddata {FIXTURES_PATH}")

    os.system("python -u manage.py runserver 0.0.0.0:8000")
