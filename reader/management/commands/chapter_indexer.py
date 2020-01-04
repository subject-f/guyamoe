from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from reader.models import Series, Chapter, ChapterIndex
import json
import os

class Command(BaseCommand):
    help = 'Index pages and chapters'

    def add_arguments(self, parser):
        parser.add_argument('series')
        parser.add_argument('file')
        parser.add_argument('--update', nargs='?')
        parser.add_argument('--delete', nargs='?')
        parser.add_argument('--list', nargs='?')

    def handle(self, *args, **options):
        if options['update']:
            chapter_number = float(options['update'])
            series = Series.objects.get(slug=options['series'])
            ch_obj = Chapter.objects.filter(chapter_number=chapter_number, series__slug=options['series']).first()
            if ch_obj:
                print("Adding chapter index to db.")
                with open(options['file'], encoding='utf-8-sig') as f:
                    data = json.load(f)["MentionedWordLocation"]
                for word in data:
                    index = ChapterIndex.objects.filter(word=word, series=series).first()
                    if not index:
                        index = ChapterIndex.objects.create(word=word, chapter_and_pages={}, series=series)
                        json_data = {}
                    index.chapter_and_pages[ch_obj.slug_chapter_number()] = data[word]
                    index.save()
                print("Finished adding chapter index to db.")
            else:
                print("Chapter does not exist.")
        elif options['delete']:
            chapter_number = float(options['delete'])
            series = Series.objects.get(slug=options['series'])
            ch_obj = Chapter.objects.filter(chapter_number=chapter_number, series__slug=options['series'], series=series).first()
            if ch_obj:
                ch_slug = ch_obj.slug_chapter_number()
                print("Deleting chapter index from db.")
                for index in ChapterIndex.objects.filter(series=series):
                    if ch_slug in index.chapter_and_pages:
                        print(index.word, index.chapter_and_pages[ch_slug])
                        del index.chapter_and_pages[ch_slug]
                        index.save()
                print("Finished deleting chapter index from db.")
            else:
                print("Chapter does not exist.")
        elif options['list']:
            chapter_number = float(options['list'])
            series = Series.objects.get(slug=options['series'])
            ch_obj = Chapter.objects.filter(chapter_number=chapter_number, series__slug=options['series'], series=series).first()
            if ch_obj:
                ch_slug = ch_obj.slug_chapter_number()
                print("Listing chapter index from db.")
                for index in ChapterIndex.objects.filter(series=series):
                    if ch_slug in index.chapter_and_pages:
                        print(index.word, index.chapter_and_pages[ch_slug])
            else:
                print("Chapter does not exist.")

        else:
            series = Series.objects.get(slug=options['series'])
            with open(options['file'], encoding='utf-8-sig') as f:
                data = json.load(f)["MentionedWordLocation"]
                for word in data:
                    ChapterIndex.objects.create(word=word, chapter_and_pages=data[word], series=series)

