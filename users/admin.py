from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, EmailVerificationToken, PasswordResetToken

class CustomUserAdmin(UserAdmin):
    list_display = ('full_name', 'username', 'email', 'is_active', 'date_joined', 'display_profile_picture')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture', 'phone_number', 'bio', 'birthdate', 'country')}),
        ('Social', {'fields': ('facebook_profile',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    fieldsets = (
        ('User Information', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'country')
        }),
        ('Profile Information', {
            'fields': ('profile_picture', 'bio', 'birthdate', 'facebook_profile')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "N/A"
    full_name.short_description = 'Full Name'

    def display_profile_picture(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', obj.profile_picture.url)
        return "No Picture"
    display_profile_picture.short_description = 'Profile Picture'

class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_valid')
    search_fields = ('user__username', 'user__email', 'token')
    list_filter = ('created_at',)
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_valid')
    
    def has_add_permission(self, request):
        return False

class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used', 'is_valid')
    search_fields = ('user__username', 'user__email', 'token')
    list_filter = ('created_at', 'is_used')
    readonly_fields = ('token', 'created_at', 'expires_at', 'is_valid')
    
    def has_add_permission(self, request):
        return False

admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerificationToken, EmailVerificationTokenAdmin)
admin.site.register(PasswordResetToken, PasswordResetTokenAdmin)
