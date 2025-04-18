from django.db import models
from pages.models import Page
from users.models import User

PERMISSION_CHOICES = (
    ("view", "View"),
    ("edit", "Edit"),
)


class SharedPage(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="shared_entries")
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_pages")
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("page", "shared_with")
