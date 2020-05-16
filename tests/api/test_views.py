import json
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import RequestFactory
from django.test import TestCase
from django.test import Client
from django.core.exceptions import ObjectDoesNotExist
from api.api import ENCODE_STR_SLASH
from tests.helpers.utils import flush_cache, APIResponseTestCase
from tests.data.mangadex import *
from tests.data.nhentai import *
from tests.data.foolslide import *
from unittest.mock import patch


class SeriesAPITestCase(APIResponseTestCase):
    fixtures = ["reader_fixtures.json"]
    main_slug = "Kaguya-Wants-To-Be-Confessed-To"
    doujin_slug = "Kaguya-Wants-To-Be-Confessed-To-Official-Doujin"
    fourkoma_slug = "We-Want-To-Talk-About-Kaguya"

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    @flush_cache
    def test_get_kaguya_main_series(self):
        # We'll follow the redirect rather than testing the path with trailing slash
        response = self.client.get(f"/api/series/{self.main_slug}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_get_kaguya_doujin(self):
        response = self.client.get(f"/api/series/{self.doujin_slug}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_get_kaguya_fourkoma(self):
        response = self.client.get(f"/api/series/{self.fourkoma_slug}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_nonexistent_series(self):
        with self.assertRaises(ObjectDoesNotExist):
            self.client.get(f"/api/series/5bun", follow=True)

    @flush_cache
    def test_get_all_series(self):
        response = self.client.get(f"/api/get_all_series", follow=True)
        self.assertEquals(response.status_code, 200)
        response = json.loads(response.content)
        expected_slugs = [self.main_slug, self.doujin_slug, self.fourkoma_slug]
        for metadata in response.values():
            self.assertTrue(metadata["slug"] in expected_slugs)
    
    @flush_cache
    def test_get_kaguya_main_series_group(self):
        # For reproducibility, just verify that it doesn't return an empty array since
        # fixtures can (and should) change in the future; empty arrays will cause problems
        response = self.client.get(f"/api/get_groups/{self.main_slug}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)["groups"]) > 0)

    @flush_cache
    def test_get_kaguya_doujin_group(self):
        response = self.client.get(f"/api/get_groups/{self.doujin_slug}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)["groups"]) > 0)

    @flush_cache
    def test_get_kaguya_fourkoma_group(self):
        response = self.client.get(f"/api/get_groups/{self.fourkoma_slug}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)["groups"]) > 0)

    @flush_cache
    def test_nonexistent_series_group(self):
        response = self.client.get(f"/api/get_groups/5bun", follow=True)
        # TODO Should this return a 404 instead?
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(json.loads(response.content)["groups"]) == 0)

    @flush_cache
    def test_get_all_groups(self):
        response = self.client.get(f"/api/get_all_groups", follow=True)
        self.assertEquals(response.status_code, 200)
        # TODO Realistically it's a bit weird the API responds without
        # a nested array in this case
        self.assertTrue(len(json.loads(response.content)) > 0)

    @flush_cache
    def test_md_series_data(self):
        pass

    # TODO
    # download_chapter/:slug/:chapter
    @flush_cache
    def test_download_chapter(self):
        pass

    # get_volume_covers/:slug
    @flush_cache
    def test_get_volume_covers(self):
        pass
    
    # search_index/:slug
    @flush_cache
    def test_search_index(self):
        pass

    # black_hole_mail
    @flush_cache
    def test_black_hole_mail(self):
        pass

class MangadexAPITestCase(APIResponseTestCase):
    def setUp(self):
        self.patch = patch("api.api.get_md_data")
        self.mock_get_md_data = self.patch.start()
        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self):
        self.patch.stop()

    @flush_cache
    def test_get_oneshot_series_data(self):
        self.mock_get_md_data.return_value = oneshot()
        response = self.client.get("/api/md_series/1", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_get_decimal_series_data(self):
        self.mock_get_md_data.return_value = decimal_chapters()
        response = self.client.get("/api/md_series/1", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_get_normal_series_data(self):
        self.mock_get_md_data.return_value = normal_series()
        response = self.client.get("/api/md_series/1", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_get_failed_md_call(self):
        self.mock_get_md_data.return_value = failed_call()
        response = self.client.get("/api/md_series/1", follow=True)
        # TODO It succeeds but returns nothing. Maybe it shouldn't?
        self.assertEquals(response.status_code, 200)
        self.assertIsNone(json.loads(response.content))

    @flush_cache
    def test_non_numeric_md_series(self):
        response = self.client.get("/api/md_series/a", follow=True)
        self.assertEquals(response.status_code, 404)

    @flush_cache
    def test_get_chapter_data_oneshot(self):
        self.mock_get_md_data.return_value = oneshot_chapter()
        response = self.client.get("/api/md_chapter_pages/1", follow=True)
        self.assertEquals(len(json.loads(response.content)), 34)

    @flush_cache
    def test_get_chapter_data_decimal(self):
        self.mock_get_md_data.return_value = decimal_chapter()
        response = self.client.get("/api/md_chapter_pages/1", follow=True)
        self.assertEquals(len(json.loads(response.content)), 18)

    @flush_cache
    def test_get_chapter_data_normal(self):
        self.mock_get_md_data.return_value = normal_chapter()
        response = self.client.get("/api/md_chapter_pages/1", follow=True)
        self.assertEquals(len(json.loads(response.content)), 3)

    @flush_cache
    def test_failed_md_chapter(self):
        self.mock_get_md_data.return_value = failed_call()
        response = self.client.get(f"/api/md_chapter_pages/1", follow=True)
        self.assertEquals(response.status_code, 503)

    
    @flush_cache
    def test_non_numeric_md_chapter(self):
        response = self.client.get("/api/md_chapter_pages/a", follow=True)
        self.assertEquals(response.status_code, 404)

class NHAPITestCase(APIResponseTestCase):
    def setUp(self):
        self.patch = patch("requests.get")
        self.mock_requests_get = self.patch.start()
        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self):
        self.patch.stop()

    @flush_cache
    def test_nh_series(self):
        self.mock_requests_get.return_value = infamous()
        response = self.client.get("/api/nh_series/1", follow=True)
        self.verify_response(json.loads(response.content))
    
    @flush_cache
    def test_failed_call(self):
        self.mock_requests_get.return_value = failed_call()
        response = self.client.get("/api/nh_series/1", follow=True)
        # TODO It succeeds but returns nothing. Maybe it shouldn't?
        self.assertEquals(response.status_code, 200)
        self.assertIsNone(json.loads(response.content))

    @flush_cache
    def test_non_numeric_nh(self):
        response = self.client.get("/api/nh_series/a", follow=True)
        self.assertEquals(response.status_code, 404)

class FoolslideAPITestCase(APIResponseTestCase):
    def setUp(self):
        self.patch_get = patch("requests.get")
        self.patch_post = patch("requests.post")
        self.mock_requests_get = self.patch_get.start()
        self.mock_requests_post = self.patch_post.start()
        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self):
        self.patch_get.stop()
        self.patch_post.stop()

    @flush_cache
    def test_encoded_url(self):
        url = "https://jaiminisbox.com/reader/series/kaguya-wants-to-be-confessed-to"
        response = self.client.get(f"/api/fs_encode_url/{url}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue("/" not in json.loads(response.content)["url"])

    @flush_cache
    def test_fs_series_invalid_url(self):
        response = self.client.get(f"/api/fs_series/1", follow=True)
        self.assertEquals(response.status_code, 400)

    @flush_cache
    def test_fs_chapter_invalid_url(self):
        response = self.client.get(f"/api/fs_chapter_pages/1", follow=True)
        self.assertEquals(response.status_code, 400)

    @flush_cache
    def test_fs_series(self):
        self.mock_requests_post.return_value = jb_kaguya()
        response = self.client.get(f"/api/fs_series/1{ENCODE_STR_SLASH}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.verify_response(json.loads(response.content))

    @flush_cache
    def test_fs_chapter(self):
        self.mock_requests_get.return_value = jb_kaguya_chapter()
        response = self.client.get(f"/api/fs_chapter_pages/1{ENCODE_STR_SLASH}", follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(json.loads(response.content)), 11)

    @flush_cache
    def test_failed_fs_series(self):
        self.mock_requests_post.return_value = failed_call()
        response = self.client.get(f"/api/fs_series/1{ENCODE_STR_SLASH}", follow=True)
        # TODO It succeeds but returns nothing. Maybe it shouldn't?
        self.assertEquals(response.status_code, 200)
        self.assertIsNone(json.loads(response.content))

    @flush_cache
    def test_failed_fs_chapter(self):
        self.mock_requests_get.return_value = failed_call()
        response = self.client.get(f"/api/fs_chapter_pages/1{ENCODE_STR_SLASH}", follow=True)
        self.assertEquals(response.status_code, 503)

# TODO
class StaffFunctionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @flush_cache
    def test_clear_cache_get_anon(self):
        pass

    @flush_cache
    def test_clear_cache_post_anon(self):
        pass

    @flush_cache
    def test_clear_cache_get_staff(self):
        pass

    @flush_cache
    def test_clear_cache_post_staff(self):
        pass

    @flush_cache
    def test_upload_new_chapter_get_anon(self):
        pass

    @flush_cache
    def test_upload_new_chapter_post_anon(self):
        pass

    @flush_cache
    def test_upload_new_chapter_get_staff(self):
        pass

    @flush_cache
    def test_upload_new_chapter_post_staff(self):
        pass