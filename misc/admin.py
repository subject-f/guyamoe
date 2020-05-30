from django.contrib import admin
from .models import Page, Variable, Static

# Register your models here.


class PageAdmin(admin.ModelAdmin):
    ordering = ("date",)
    list_display = (
        "page_title",
        "page_url",
        "cover_image_url",
        "date",
    )
    filter_horizontal = ("variable",)


class StaticAdmin(admin.ModelAdmin):
    list_display = (
        "static_file",
        "page",
    )


admin.site.register(Page, PageAdmin)
admin.site.register(Variable)
admin.site.register(Static, StaticAdmin)
