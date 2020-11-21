from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.html import format_html

from banners.models import Banner


@admin.register(Banner)
class BannerAdmin(SortableAdminMixin, admin.ModelAdmin):
    indexCnt = 0
    model = Banner
    readonly_fields = ['preview']
    list_display = ['show_number', 'title', 'text', 'status', 'preview']
    list_display_links = ['show_number', 'title', 'text']
    search_fields = ['title']

    def preview(self, obj):
        if obj.src:
            return format_html('<img src="{}" height="100"/>', obj.src.url)
        else:
            return "Здесь будет превью, когда вы выберете файл."
    preview.short_description = 'превью'

    def show_number(self, obj):
        count = Banner.objects.all().count()
        if self.indexCnt < count:
            self.indexCnt += 1
        else:
            self.indexCnt = 1
        return self.indexCnt
    show_number.short_description = '№'
