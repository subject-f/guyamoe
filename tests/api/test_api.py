import json
from tests.helpers.utils import flush_cache, APIResponseTestCase
from django.core.cache import cache
from tests.data.mangadex import *
from tests.data.nhentai import *
from tests.data.foolslide import *
from django.test import TestCase
from unittest.mock import patch
from django.test.client import RequestFactory
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from time import sleep
from api.api import *


class EtagTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def get_chapter_tag(self, slug):
        return f"{slug}_chapter_data_etag"

    @flush_cache
    def test_all_chapter_data_etag(self):
        tag = "all_chapter_data_etag"
        self.assertIsNone(cache.get(tag))
        all_chapter_data_etag(self.factory.get("/chapter"))
        self.assertIsNotNone(cache.get(tag))

    @flush_cache
    def test_chapter_data_etag(self):
        slug = "kaguya-gonewild"
        tag = self.get_chapter_tag(slug)
        self.assertIsNone(cache.get(tag))
        chapter_data_etag(self.factory.get("/chapter"), slug)
        self.assertIsNotNone(cache.get(tag))

    @flush_cache
    def test_chapter_data_etag_different_slug(self):
        slug_1 = "kaguya-gonewild"
        tag_1 = self.get_chapter_tag(slug_1)
        self.assertIsNone(cache.get(tag_1))
        chapter_data_etag(self.factory.get("/chapter"), slug_1)
        self.assertIsNotNone(cache.get(tag_1))
        slug_2 = "kei-gonewild"
        tag_2 = self.get_chapter_tag(slug_2)
        self.assertIsNone(cache.get(tag_2))
        chapter_data_etag(self.factory.get("/chapter"), slug_2)
        self.assertIsNotNone(cache.get(tag_1))
        self.assertIsNotNone(cache.get(tag_2))


# Realistically this group of tests only ensures the fixture is read correctly
# so it doesn't really do anything useful except making sure the fixtures that'll
# make the homepage load are, in fact, there
class SeriesDataTestCase(APIResponseTestCase):
    fixtures = ["reader_fixtures.json"]
    main_slug = "Kaguya-Wants-To-Be-Confessed-To"
    doujin_slug = "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"
    fourkoma_slug = "We-Want-To-Talk-About-Kaguya"

    def test_get_kaguya_main_series(self):
        slug = self.main_slug
        data = series_data(slug)
        self.assertEquals(data["slug"], slug)
        self.verify_response(data)

    def test_get_kaguya_doujin(self):
        slug = self.doujin_slug
        data = series_data(slug)
        self.assertEquals(data["slug"], slug)
        self.verify_response(data)

    def test_get_kaguya_fourkoma(self):
        slug = self.fourkoma_slug
        data = series_data(slug)
        self.assertEquals(data["slug"], slug)
        self.verify_response(data)

    def test_non_existent_series(self):
        with self.assertRaises(ObjectDoesNotExist):
            slug = self.main_slug
            series_data("Kei-Wants-To-Be-Confessed-To")

    @flush_cache
    def test_series_data_cache(self):
        slug = self.main_slug
        series_data_cache(slug)
        cached = cache.get(f"series_api_data_{slug}")
        self.assertIsNotNone(cached)
        self.verify_response(cached)

    @flush_cache
    def test_all_groups(self):
        groups = all_groups()
        # It shouldn't throw an exception, basically
        self.assertTrue(True)
        # And verify that it's cached. Basically, memcached
        # should be running for these tests
        self.assertIsNotNone(cache.get("all_groups_data"))

class MiscTestCase(TestCase):
    def test_random_chars(self):
        self.assertEquals(len(random_chars()), 8)
    
    def test_get_md_data(self):
        with patch("requests.get") as mock_requests:
            test_url = "https://guya.moe"
            headers = {
                'Referer': 'https://mangadex.org',
                'User-Agent': 'Mozilla Firefox Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0.'
            }
            get_md_data(test_url)
            mock_requests.assert_called_once_with(test_url, headers=headers)
    
    @flush_cache
    def test_clear_pages_cache(self):
        cache.set("random_cache_data", "test", 600)
        cache.set("online_now", set(["1", "2"]), 600)
        cache.set("1", "1", 600)
        cache.set("peak_traffic", 100, 600)
        self.assertEquals(cache.get("random_cache_data"), "test")
        clear_pages_cache()
        self.assertIsNone(cache.get("random_cache_data"))
        self.assertTrue("1" in cache.get("online_now"))
        self.assertTrue("2" not in cache.get("online_now"))
        self.assertEquals(cache.get("peak_traffic"), 100)

    @flush_cache
    def test_clear_series_cache(self):
        series_slug = "slug"
        cache.set(f"series_api_data_{series_slug}", "test", 600)
        cache.set(f"series_page_data_{series_slug}", "test", 600)
        cache.set(f"groups_data_{series_slug}", "test", 600)
        cache.set(f"vol_covers_{series_slug}", "test", 600)

        self.assertIsNotNone(cache.get(f"series_api_data_{series_slug}"))
        self.assertIsNotNone(cache.get(f"series_page_data_{series_slug}"))
        self.assertIsNotNone(cache.get(f"groups_data_{series_slug}"))
        self.assertIsNotNone(cache.get(f"vol_covers_{series_slug}"))

        clear_series_cache(series_slug)

        self.assertIsNone(cache.get(f"series_api_data_{series_slug}"))
        self.assertIsNone(cache.get(f"series_page_data_{series_slug}"))
        self.assertIsNone(cache.get(f"groups_data_{series_slug}"))
        self.assertIsNone(cache.get(f"vol_covers_{series_slug}"))


class MangadexTestCase(APIResponseTestCase):
    def setUp(self):
        self.patch = patch("api.api.get_md_data")
        self.mock_get_md_data = self.patch.start()

    def tearDown(self):
        self.patch.stop()

    def verify_series_response(self, response, expected_data):
        self.assertEquals(response["title"], expected_data["manga"]["title"])
        self.assertEquals(
            response["description"], expected_data["manga"]["description"]
        )
        self.assertEquals(response["author"], expected_data["manga"]["author"])
        self.assertEquals(response["artist"], expected_data["manga"]["artist"])
        # The groups from the expected data should be a superset
        # of our response after filtering for language
        available_groups = set(
            map(lambda v: v["group_name"], expected_data["group"].values())
        )
        for group in response["groups"].values():
            self.assertTrue(group in available_groups)
        self.assertTrue(expected_data["manga"]["cover_url"] in response["cover"])
        self.assertTrue("preferred_sort" in response)
        # We'll test the reverse here with the response matching
        # up with our expected data
        for chapter, metadata in response["chapters"].items():
            # Oneshot functionality, where it's a less-than-one decimal
            oneshot = False
            if float(chapter) < 0.09 and float(chapter) > 0.01:
                oneshot = True

            for group, chapter_id in metadata["groups"].items():
                self.assertTrue(group in response["groups"])
                self.assertTrue(chapter_id in expected_data["chapter"])
                self.assertEquals(
                    expected_data["chapter"][chapter_id]["title"], metadata["title"]
                )
                volume = expected_data["chapter"][chapter_id]["volume"]
                self.assertEquals(
                    metadata["volume"], volume if volume else "Uncategorized"
                )
                if oneshot:
                    chapter = chapter[3:]
                    self.assertEquals(
                        int(chapter), expected_data["chapter"][chapter_id]["timestamp"]
                    )
                else:
                    self.assertEquals(
                        chapter, expected_data["chapter"][chapter_id]["chapter"]
                    )

    @flush_cache
    def test_get_oneshot_series_data(self):
        resp = oneshot()
        self.mock_get_md_data.return_value = resp
        expected_data = json.loads(resp.text)
        response = md_series_data("1")
        self.verify_series_response(response, expected_data)
        self.verify_response(response)

    @flush_cache
    def test_get_decimal_series_data(self):
        resp = decimal_chapters()
        self.mock_get_md_data.return_value = resp
        expected_data = json.loads(resp.text)
        response = md_series_data("1")
        self.verify_series_response(response, expected_data)
        self.verify_response(response)

    @flush_cache
    def test_get_normal_series_data(self):
        resp = normal_series()
        self.mock_get_md_data.return_value = resp
        expected_data = json.loads(resp.text)
        response = md_series_data("1")
        self.verify_series_response(response, expected_data)
        self.verify_response(response)

    @flush_cache
    def test_verify_cache_cleared(self):
        resp = normal_series()
        self.mock_get_md_data.return_value = resp
        expected_data = json.loads(resp.text)
        response = md_series_data("1")
        self.verify_series_response(response, expected_data)
        self.verify_response(response)
        cache.clear()
        self.mock_get_md_data.return_value = None
        with self.assertRaises(AttributeError):
            md_series_data("1")

    @flush_cache
    def test_verify_cache_intact(self):
        resp = normal_series()
        self.mock_get_md_data.return_value = resp
        expected_data = json.loads(resp.text)
        response = md_series_data("1")
        self.verify_series_response(response, expected_data)
        self.verify_response(response)
        self.mock_get_md_data.return_value = None
        response = md_series_data("1")
        self.verify_series_response(response, expected_data)
        self.verify_response(response)

    @flush_cache
    def test_get_failed_md_call(self):
        resp = failed_call()
        self.mock_get_md_data.return_value = resp
        response = md_series_data("1")
        self.assertIsNone(response)

    @flush_cache
    def test_get_chapter_data_oneshot(self):
        resp = oneshot_chapter()
        expected_value = json.loads(resp.text)
        self.mock_get_md_data.return_value = resp
        response = md_chapter_data("1")
        self.assertEquals(len(response["pages"]), 34)
        self.assertEquals(response["series_id"], expected_value["manga_id"])
        self.assertEquals(response["chapter"][3:], str(expected_value["timestamp"]))

    @flush_cache
    def test_get_chapter_data_decimal(self):
        resp = decimal_chapter()
        expected_value = json.loads(resp.text)
        self.mock_get_md_data.return_value = resp
        response = md_chapter_data("1")
        self.assertEquals(len(response["pages"]), 18)
        self.assertEquals(response["series_id"], expected_value["manga_id"])
        self.assertEquals(response["chapter"], expected_value["chapter"])

    @flush_cache
    def test_get_chapter_data_normal(self):
        resp = normal_chapter()
        expected_value = json.loads(resp.text)
        self.mock_get_md_data.return_value = resp
        response = md_chapter_data("1")
        self.assertEquals(len(response["pages"]), 3)
        self.assertEquals(response["series_id"], expected_value["manga_id"])
        self.assertEquals(response["chapter"], expected_value["chapter"])

class NHTestCase(APIResponseTestCase):
    def setUp(self):
        self.patch = patch("requests.get")
        self.mock_requests_get = self.patch.start()

    def tearDown(self):
        self.patch.stop()

    @flush_cache
    def test_nh_series(self):
        resp = infamous()
        self.mock_requests_get.return_value = resp
        response = nh_series_data("1")
        self.verify_response(response)
        self.assertTrue("timestamp" in response)
    
    @flush_cache
    def test_failed_call(self):
        self.mock_requests_get.return_value = failed_call()
        response = nh_series_data("1")
        self.assertIsNone(response)

class FoolslideTestCase(APIResponseTestCase):
    def setUp(self):
        self.patch_get = patch("requests.get")
        self.patch_post = patch("requests.post")
        self.mock_requests_get = self.patch_get.start()
        self.mock_requests_post = self.patch_post.start()

    def tearDown(self):
        self.patch_get.stop()
        self.patch_post.stop()

    @flush_cache
    def test_jb_kaguya(self):
        self.mock_requests_post.return_value = jb_kaguya()
        response = fs_series_data("1")
        self.verify_response(response)
    
    @flush_cache
    def test_jb_kaguya_chapter(self):
        self.mock_requests_get.return_value = jb_kaguya_chapter()
        response = fs_chapter_data("1")
        # 11 pages
        self.assertEquals(len(response), 11)

    @flush_cache
    def test_helvetica_zombies(self):
        self.mock_requests_post.return_value = helvetica_zombies()
        response = fs_series_data("1")
        self.verify_response(response)

    @flush_cache
    def test_helvetica_zombies_chapter(self):
        self.mock_requests_get.return_value = helvetica_zombies_chapter()
        response = fs_chapter_data("1")
        # 39 pages
        self.assertEquals(len(response), 39)

    def test_encode_url(self):
        url = "//?".replace("/", ENCODE_STR_SLASH).replace("?", ENCODE_STR_QUESTION)
        self.assertEquals(fs_encode_url("//?") , url)

    def test_decode_url(self):
        url = f"{ENCODE_STR_SLASH}{ENCODE_STR_QUESTION}"
        self.assertEquals(fs_decode_url(url), "/?")

    def test_fs_encode_slug_1(self):
        url = "https://helveticascans.com/r/read/zombie-100/"
        self.assertEquals(fs_encode_slug(url), "helveticascans.com/r/series/zombie-100".replace("/", ENCODE_STR_SLASH))
    
    def test_fs_encode_slug_2(self):
        url = "https://jaiminisbox.com/reader/series/kaguya-wants-to-be-confessed-to"
        self.assertEquals(fs_encode_slug(url), "jaiminisbox.com/reader/series/kaguya-wants-to-be-confessed-to".replace("/", ENCODE_STR_SLASH))

# TODO
class FileOpsTestCase(TestCase):
    @flush_cache
    def test_zip_volume(self):
        pass

    @flush_cache
    def test_zip_chapter(self):
        pass

    @flush_cache
    def test_create_preview_pages(self):
        pass