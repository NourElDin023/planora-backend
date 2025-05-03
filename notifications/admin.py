from django.contrib import admin
from .models import Notification
from django.utils.html import format_html

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('short_message', 'recipient', 'sender', 'timestamp', 'is_read', 'view_link')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('message', 'recipient__username', 'sender__username')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'view_link')
    list_editable = ['is_read']
    autocomplete_fields = ['recipient', 'sender']
    list_per_page = 30
    
    fieldsets = (
        ('Message Details', {
            'fields': ('message', 'link', 'view_link'),
        }),
        ('Users', {
            'fields': ('recipient', 'sender'),
        }),
        ('Status', {
            'fields': ('is_read', 'timestamp'),
        }),
    )
    
    def short_message(self, obj):
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    
    short_message.short_description = 'Message'
    
    def view_link(self, obj):
        if obj.link:
            return format_html('<a href="{}" target="_blank">View</a>', obj.link)
        return "-"
    
    view_link.short_description = 'Link'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'sender')
