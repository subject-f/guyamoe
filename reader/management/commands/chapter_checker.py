from django.core.management.base import BaseCommand

from reader.models import Series
from reader.scraper.mappings import SCRAPER_MAPPINGS


class Command(BaseCommand):
    help = "Import new chapters from JaiminisBox and Mangadex"

    def add_arguments(self, parser):
        # # Positional arguments
        parser.add_argument("--lookup", nargs="?", default="all")
        parser.add_argument("--update", action="store_true")
        parser.add_argument("--series", nargs="?")
        parser.add_argument("--chapters", nargs="+")

    def handle(self, *args, **options):
        if options["update"] and options["series"] and options["chapters"]:
            chapters = options["chapters"]
            chapters_and_groups = {}
            for chapter in chapters:
                chapter_number, group_name = chapter.split(" ", 1)
                if float(chapter_number) not in chapters_and_groups:
                    chapters_and_groups[float(chapter_number)] = [group_name]
                else:
                    chapters_and_groups[float(chapter_number)].append(group_name)
            series = Series.objects.get(slug=options["series"])
            scraper_class = SCRAPER_MAPPINGS.get(series.scraping_source, None)
            if not scraper_class and options["lookup"]:
                scraper_class = SCRAPER_MAPPINGS.get(options["lookup"], None)
                if not scraper_class:
                    print("Could not find specified scraping source.")
            scraper = scraper_class(series)
            if scraper.initialized:
                scraper.scrape_chapters(
                    check_updates=True, specific_chapters=chapters_and_groups
                )
        else:
            check_updates = options["update"]
            for series in Series.objects.filter(scraping_enabled=True):
                scraper_class = SCRAPER_MAPPINGS[series.scraping_source]
                scraper = scraper_class(series)
                if scraper.initialized:
                    scraper.scrape_chapters(check_updates=check_updates)
