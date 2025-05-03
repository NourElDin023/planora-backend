from django.contrib import admin
from .models import Collection
from django.utils.html import format_html


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'is_link_shareable', 'shareable_permission', 'active', 'task_count')
    list_filter = ('active', 'is_link_shareable', 'shareable_permission', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'shareable_link', 'task_count')
    list_editable = ['active']
    autocomplete_fields = ['owner']
    
    fieldsets = (
        ('Collection Information', {
            'fields': ('title', 'description'),
        }),
        ('Ownership', {
            'fields': ('owner',),
        }),
        ('Sharing Settings', {
            'fields': ('is_link_shareable', 'shareable_link_token', 'shareable_link', 'shareable_permission'),
        }),
        ('Status', {
            'fields': ('active', 'task_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def shareable_link(self, obj):
        if obj.is_link_shareable:
            return format_html(
                '<a href="/share/{}" target="_blank">/share/{}</a>',
                obj.shareable_link_token,
                obj.shareable_link_token
            )
        return "Sharing disabled"
    
    shareable_link.short_description = 'Shareable Link'
    
    def task_count(self, obj):
        return obj.tasks.count()
    
    task_count.short_description = 'Number of Tasks'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner').prefetch_related('tasks')


admin.site.register(Collection, CollectionAdmin)
