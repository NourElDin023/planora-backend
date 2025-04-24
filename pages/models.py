from django.db import models
from users.models import User
import uuid

PERMISSION_CHOICES = (
    ("view", "View"),
    ("edit", "Edit"),
)


class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_link_shareable = models.BooleanField(default=False)
    shareable_link_token = models.UUIDField(default=uuid.uuid4, unique=True)
    shareable_permission = models.CharField(
        max_length=10, choices=PERMISSION_CHOICES, default="view"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
