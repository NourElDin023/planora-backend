from django.contrib import admin
from .models import Task
from django.utils.html import format_html

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner',
        'start_time', 'end_time', 'due_date',
        'category', 'completed', 'collection',
        'created_at'
    )
    list_filter = (
        'completed', 'category',
        'start_time', 'end_time', 'due_date',
        'created_at', 'collection'
    )
    search_fields = ('title', 'details', 'category', 'owner__username')
    date_hierarchy = 'due_date'
    ordering = ('-due_date',)
    readonly_fields = ('created_at', 'updated_at', 'task_icon_preview')
    autocomplete_fields = ['owner', 'collection']
    list_editable = ['completed']
    list_per_page = 25

    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'details', 'category', 'task_icon', 'task_icon_preview'),
        }),
        ('Schedule', {
            'fields': ('start_time', 'end_time', 'due_date'),
        }),
        ('Status', {
            'fields': ('completed',),
        }),
        ('Relationships', {
            'fields': ('owner', 'collection'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def task_icon_preview(self, obj):
        if obj.task_icon:
            return format_html('<img src="{}" width="100" />', obj.task_icon.url)
        return "No Image"

    task_icon_preview.short_description = 'Task Icon Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'collection')
