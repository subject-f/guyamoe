from django.conf import settings

def branding(request):
    return {
        "brand": {
            "name": settings.BRANDING_NAME,
            "description": settings.BRANDING_DESCRIPTION,
            "image_url": settings.BRANDING_IMAGE_URL,
        }
    }
