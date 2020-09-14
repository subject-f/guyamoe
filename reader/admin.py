from datetime import datetime, timezone

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
    list_display = (
        "chapter_number",
        "title",
        "series",
        "volume",
        "version",
        "time_since_last_update",
        "updated_on",
        "uploaded_on",
    )

    def get_queryset(self, request):
        qs = super(ChapterAdmin, self).get_queryset(request)
        sort_sql = """SELECT
CASE
    WHEN updated_on IS NOT NULL THEN updated_on
    ELSE uploaded_on END
as time_since_change
"""
        qs = qs.extra(select={"time_since_last_update": sort_sql}).order_by(
            "-time_since_last_update"
        )
        return qs

    def time_since_last_update(self, obj):
        if obj.time_since_last_update is not None:
            try:
                time_diff = datetime.strptime(
                    obj.time_since_last_update, "%Y-%m-%d %H:%M:%S.%f"
                )
            except ValueError:
                time_diff = datetime.strptime(
                    obj.time_since_last_update, "%Y-%m-%d %H:%M:%S"
                )
            time_diff = time_diff.replace(tzinfo=timezone.utc)
            curr_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            time_since_last_update = curr_time - time_diff
        else:
            time_since_last_update = curr_time - obj.uploaded_on
        days = time_since_last_update.days
        seconds = time_since_last_update.seconds
        hours = seconds // 3600
        minutes = (seconds // 60) % 60

        return f"{days} days {hours} hours {minutes} mins"

    time_since_last_update.admin_order_field = "time_since_last_update"
    ordering = ("-uploaded_on", "-updated_on")


admin.site.register(Chapter, ChapterAdmin)
