from django.contrib import admin
from .models import Series, Chapter

# Register your models here.
admin.site.register(Series)

class ChapterAdmin(admin.ModelAdmin):
    ordering = ('chapter_number',)
    list_display = ('chapter_number', 'title', 'series', 'volume', 'page_count',)

admin.site.register(Chapter, ChapterAdmin)