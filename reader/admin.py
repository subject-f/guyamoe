from django.contrib import admin
from .models import HitCount, Person, Group, Series, Volume, Chapter

# Register your models here.
class HitCountAdmin(admin.ModelAdmin):
    ordering = ('hits',)
    list_display = ('hits', 'content', 'series', 'content_type',)
    def series(self, obj):
        print(type(obj.content))
        if isinstance(obj.content, Series):
            return obj.content.name
        else:
            return obj.content.series.name

admin.site.register(HitCount, HitCountAdmin)
admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Series)


class VolumeAdmin(admin.ModelAdmin):
    ordering = ('volume_number',)
    # list_display = ('volume_number', 'series', 'volume_cover', )

    exclude=("volume_cover ",)
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ()
        else:
            return ('volume_cover',)
admin.site.register(Volume, VolumeAdmin)

class ChapterAdmin(admin.ModelAdmin):
    ordering = ('chapter_number',)
    list_display = ('chapter_number', 'title', 'series', 'volume', 'page_count',)

admin.site.register(Chapter, ChapterAdmin)
