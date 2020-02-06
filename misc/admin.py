from django.contrib import admin
from .models import Page, Variable

# Register your models here.
class PageAdmin(admin.ModelAdmin):
    ordering = ('date',)
    list_display = ('content', 'page_title', 'page_url', 'cover_image_url', 'date',)
    filter_horizontal = ('variable',)

admin.site.register(Page, PageAdmin)
admin.site.register(Variable)