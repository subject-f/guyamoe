from django.core.cache import cache
from .users_cache_lib import get_user_ip
from django.utils.deprecation import MiddlewareMixin

class OnlineNowMiddleware(MiddlewareMixin):
    # def __init__(self, get_response):
    #     self.get_response = get_response

    def process_response(self, request, response):
        user_ip = get_user_ip(request)
        online = cache.get("online_now")
        peak_traffic = cache.get("peak_traffic")
        if not peak_traffic:
            peak_traffic = 0
        if online:
            online = set([ip for ip in online if cache.get(ip)])
        else:
            online = set([])
        cache.set(user_ip, user_ip, 600)
        online.add(user_ip)
        if len(online) > peak_traffic:
            peak_traffic = len(online)
            cache.set("peak_traffic", peak_traffic, 3600 * 8)
        cache.set("online_now", online, 600)
        # response = self.get_response(request)
        return response
