from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing task instances.
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter tasks by logged in user
        """
        return Task.objects.filter(owner=self.request.user).order_by("-due_date", "due_time")

    def perform_create(self, serializer):
        """
        Set the owner to the logged in user when creating a task
        """
        serializer.save(owner=self.request.user)
