from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUser already has:
    # - id, username, password, first_name, last_name, email
    # - is_active, is_staff, is_superuser, date_joined, last_login
    # - is_activated - we'll use Django's built-in is_active field
    # Custom fields needed
    phone_number = models.CharField(max_length=12)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    facebook_profile = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
