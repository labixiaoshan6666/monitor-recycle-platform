from django.contrib import admin
from django.utils.html import format_html
from .models import Policy, RecycleProduct


@admin.register(RecycleProduct)
class RecycleProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name_display', 'category', 'brand', 'model', 'price_display', 'scrape_date')
    list_filter = ('category', 'brand', 'scrape_date')
    search_fields = ('product_code', 'name', 'brand', 'model')
    readonly_fields = ('product_code', 'created_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('product_code', 'name', 'category', 'brand', 'model')
        }),
        ('价格信息', {
            'fields': ('avg_price', 'scrape_date', 'price_history')
        }),
        ('系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def name_display(self, obj):
        return f"{obj.brand} {obj.model}"
    name_display.short_description = "产品名称"

    def price_display(self, obj):
        return format_html('<span style="color: #2563eb; font-weight: bold;">¥{}</span>', obj.avg_price)
    price_display.short_description = "回收价格"


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'has_attachment', 'has_content')
    list_filter = ('publish_date',)
    search_fields = ('title', 'content')
    ordering = ('-publish_date',)
    fieldsets = (
        ('政策内容', {
            'fields': ('title', 'content')
        }),
        ('附件和发布', {
            'fields': ('attachment', 'publish_date')
        }),
    )

    def has_attachment(self, obj):
        if obj.attachment:
            return format_html('<span style="color: #10b981;">✓ 有附件</span>')
        return format_html('<span style="color: #9ca3af;">无附件</span>')
    has_attachment.short_description = "附件"

    def has_content(self, obj):
        if obj.content:
            return format_html('<span style="color: #10b981;">✓ 有内容</span>')
        return format_html('<span style="color: #9ca3af;">无内容</span>')
    has_content.short_description = "文字内容"

