import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

from reader.users_cache_lib import get_user_ip


class ForwardParametersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.GET.urlencode():
            response["Location"] += f"?{request.GET.urlencode()}"
        return response


class ReferralMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        ip = get_user_ip(request)
        if (
            not cache.get(f"referral_{ip}")
            and request.method == "GET"
            and request.GET.get("rid")
            and response.status_code not in [301, 302]
        ):
            # Handle only one referral from an IP at a time
            cache.set(
                f"referral_{ip}",
                {"rid": request.GET.get("rid"), "consumed": False},
                120,
            )
        return response
