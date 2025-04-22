from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
from datetime import datetime, timedelta
from django.core.validators import RegexValidator

class User(AbstractUser):
    # AbstractUser already has:
    # - id, username, password, first_name, last_name, email
    # - is_active, is_staff, is_superuser, date_joined, last_login
    # - is_activated - we'll use Django's built-in is_active field
    # Custom fields needed
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in a valid format. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    facebook_profile = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set token to expire after 24 hours by default
            self.expires_at = datetime.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_valid(self):
        return datetime.now() < self.expires_at
    
    def __str__(self):
        return f"Verification token for {self.user.username}"

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set token to expire after 1 hour
            self.expires_at = datetime.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    @property
    def is_valid(self):
        return datetime.now() < self.expires_at and not self.is_used
    
    def __str__(self):
        return f"Password reset token for {self.user.username}"
