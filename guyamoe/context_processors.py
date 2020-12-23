from django.conf import settings

def branding(request):
    return {
        "brand": {
            "name": settings.BRANDING_NAME,
            "description": settings.BRANDING_DESCRIPTION,
            "image_url": settings.BRANDING_IMAGE_URL,
        }
    }

def urls(request):
    return {
        "root_domain": settings.CANONICAL_ROOT_DOMAIN,
        "uri_scheme": request.scheme,
        "absolute_url": request.build_absolute_uri(request.path),
    }
