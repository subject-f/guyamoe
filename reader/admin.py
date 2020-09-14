from django.contrib import admin

from .forms import ChapterForm, SeriesForm
from .models import Chapter, Group, HitCount, Person, Series, Volume


# Register your models here.
class HitCountAdmin(admin.ModelAdmin):
    ordering = ("hits",)
    list_display = (
        "hits",
        "content",
        "series",
        "content_type",
    )

    def series(self, obj):
        if isinstance(obj.content, Series):
            return obj.content.name
        if isinstance(obj.content, Chapter):
            return obj.content.title
        else:
            return obj


admin.site.register(HitCount, HitCountAdmin)
admin.site.register(Person)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


admin.site.register(Group, GroupAdmin)


class SeriesAdmin(admin.ModelAdmin):
    form = SeriesForm
    list_display = ("name",)


admin.site.register(Series, SeriesAdmin)


class VolumeAdmin(admin.ModelAdmin):
    search_fields = (
        "volume_number",
        "series__name",
    )
    ordering = ("volume_number",)
    list_display = (
        "volume_number",
        "series",
        "volume_cover",
    )

    exclude = ("volume_cover ",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ()
        else:
            return ("volume_cover",)


admin.site.register(Volume, VolumeAdmin)


class ChapterAdmin(admin.ModelAdmin):
    form = ChapterForm
    search_fields = (
        "chapter_number",
        "title",
        "series__name",
        "volume",
    )
    ordering = (
        "-updated_on",
        "-uploaded_on",
    )
    list_display = (
        "chapter_number",
        "title",
        "series",
        "volume",
        "updated_on",
        "uploaded_on",
    )


admin.site.register(Chapter, ChapterAdmin)
