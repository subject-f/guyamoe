from django.core.cache import cache
from .users_cache_lib import curr_user_and_online

class OnlineNowMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ### Install and test with memcache first
        # user_ip = curr_user_and_online(request)
        # online = cache.get('online_now')
        # if online:
        #     online = [ip for ip in online if cache.get(ip)]
        # else:
        #     online = []
        # cache.set(user_ip, user_ip, 600)
        # if user_ip not in online:
        #     online.append(user_ip)
        # cache.set('online_now', online)
        # request.online_now = len(online)
        response = self.get_response(request)
        return response