from django.contrib import admin
from .models import Note
from django.utils.html import format_html

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'task', 'created_at', 'updated_at', 'short_content')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content', 'user__username', 'task__title')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['user', 'task']
    list_per_page = 25
    
    fieldsets = (
        ('Note Information', {
            'fields': ('title', 'content'),
        }),
        ('Relationships', {
            'fields': ('user', 'task'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def short_content(self, obj):
        if len(obj.content) > 75:
            return f"{obj.content[:75]}..."
        return obj.content
    
    short_content.short_description = 'Content'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'task')
