from pages.models import Collection
from django.db import models
from django.conf import settings


class Task(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    due_date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()
    
    category = models.CharField(max_length=100)
    task_icon = models.ImageField(upload_to="task_icons/", blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.title
