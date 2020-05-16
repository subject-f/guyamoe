from django.core.cache import cache
from django.test import TestCase
from django.test import Client


def flush_cache(fun):
    def wrapper(*args, **kargs):
        cache.clear()
        return fun(*args, **kargs)

    return wrapper


class Response:
    def __init__(self, text, status_code):
        self.text = text.replace("\n", "")
        self.status_code = status_code


class APIResponseTestCase(TestCase):
    def verify_response(self, response):
        self.assertTrue("slug" in response)
        self.assertTrue("title" in response)
        self.assertTrue("description" in response)
        self.assertTrue("artist" in response)
        self.assertTrue("groups" in response)
        self.assertTrue("cover" in response)
        self.assertTrue("chapters" in response)
