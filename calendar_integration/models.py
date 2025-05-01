from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class CalendarToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    token_type = models.CharField(max_length=50, default="Bearer")
    expires_in = models.IntegerField(default=3600)  # Optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calendar Token for {self.user.username}"
