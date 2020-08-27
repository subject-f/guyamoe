from django.core.cache import cache
import requests
import base64

ENCODE_STR_SLASH = "%FF-"
ENCODE_STR_QUESTION = "%DE-"
GLOBAL_HEADERS = {
    "User-Agent": "Mozilla Firefox Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0.",
}


def naive_encode(url):
    return url.replace("/", ENCODE_STR_SLASH).replace("?", ENCODE_STR_QUESTION)


def naive_decode(url):
    return url.replace(ENCODE_STR_SLASH, "/").replace(ENCODE_STR_QUESTION, "?")


def decode(url: str):
    return str(base64.urlsafe_b64decode(url.encode()), "utf-8")


def encode(url: str):
    return str(base64.urlsafe_b64encode(url.encode()), "utf-8")


def get_wrapper(url, *, headers={}, **kwargs):
    return requests.get(url, headers={**GLOBAL_HEADERS, **headers}, **kwargs)


def post_wrapper(url, headers={}, **kwargs):
    return requests.post(url, headers={**GLOBAL_HEADERS, **headers}, **kwargs)


def api_cache(*, prefix, time):
    def wrapper(f):
        def inner(self, meta_id):
            data = cache.get(f"{prefix}_{meta_id}")
            if not data:
                data = f(self, meta_id)
                if not data:
                    return None
                else:
                    cache.set(f"{prefix}_{meta_id}", data, time)
                    return data
            else:
                return data

        return inner

    return wrapper
