from django.contrib import admin
from .models import WebsiteSettings, LandingSection, SectionItem

class SectionItemInline(admin.StackedInline):
    model = SectionItem
    extra = 0
    ordering = ('order',)

@admin.register(LandingSection)
class LandingSectionAdmin(admin.ModelAdmin):
    list_display = ('website', 'section_type', 'title', 'order', 'is_active')
    list_filter = ('section_type', 'is_active', 'website')
    search_fields = ('title', 'website__catalog__title')
    inlines = [SectionItemInline]
    ordering = ('website', 'order')

@admin.register(WebsiteSettings)
class WebsiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'custom_domain', 'is_published', 'created_at')
    search_fields = ('catalog__title', 'custom_domain')
    list_filter = ('is_published',)
