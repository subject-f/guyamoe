from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.db.models import F
from django.template import Context, Template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.utils.decorators import decorator_from_middleware
import json

from reader.middleware import OnlineNowMiddleware
from reader.models import HitCount
from reader.users_cache_lib import get_user_ip
from .models import Page
from django.conf import settings


@csrf_exempt
@decorator_from_middleware(OnlineNowMiddleware)
def hit_count(request):
    if request.method == "POST":
        user_ip = get_user_ip(request)
        page_id = f"url_{request.POST['page_url']}/{user_ip}"
        if not cache.get(page_id):
            cache.set(page_id, page_id, 60)
            page_url = request.POST["page_url"]
            page_id = Page.objects.get(page_url=page_url).id
            page = ContentType.objects.get(app_label="misc", model="page")
            hit, _ = HitCount.objects.get_or_create(
                content_type=page, object_id=page_id
            )
            hit.hits = F("hits") + 1
            hit.save()

    return HttpResponse(json.dumps({}), content_type="application/json")


@cache_control(public=True, max_age=3600, s_maxage=60)
@decorator_from_middleware(OnlineNowMiddleware)
def content(request, page_url):
    try:
        page = Page.objects.get(page_url=page_url)
    except Page.DoesNotExist:
        raise Http404("Page does not exist.")
    content = page.content
    for var in page.variable.all():
        content = content.replace("{{%s}}" % var.key, var.value)
    template_tags = {
        "content": content,
        "page_url": page.page_url,
        "page_title": page.page_title,
        "date": int(page.date.timestamp()) if page.date else "",
        "cover_image_url": page.cover_image_url,
        "template": "misc_pages_list",
        "static_dir": f"/media/pages/{page.page_url}/static/",
        "relative_url": f"pages/{page_url}/",
        "version_query": settings.STATIC_VERSION,
    }
    if page.standalone:
        template = Template(page.content)
        return HttpResponse(
            template.render(Context(template_tags)), content_type="text/html"
        )
    else:
        return render(request, "misc/misc.html", template_tags)


@cache_control(public=True, max_age=300, s_maxage=60)
@decorator_from_middleware(OnlineNowMiddleware)
def misc_pages(request):
    pages = cache.get("misc_pages")
    if not pages:
        pages = Page.objects.filter(hidden=False).order_by("-date")
        cache.set("misc_pages", pages, 3600 * 8)
    for page in pages:
        page.date = int(page.date.timestamp()) if page.date else ""
    return render(
        request,
        "misc/misc_pages.html",
        {
            "pages": pages,
            "template": "misc_page",
            "relative_url": "pages/",
            "version_query": settings.STATIC_VERSION,
        },
    )
