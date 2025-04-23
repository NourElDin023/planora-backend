# views.py (Django)
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer
from sharing.models import SharedPage
from pages.models import Collection


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all collections the user can access
        accessible_collections = Collection.objects.filter(
            Q(owner=user)
            | Q(shared_entries__shared_with=user)
            | (Q(is_link_shareable=True) & Q(shareable_permission__in=["view", "edit"]))
        ).distinct()

        # Filter tasks based on collection access and optional collection filter
        collection_id = self.request.query_params.get("collection")
        if collection_id:
            if not accessible_collections.filter(id=collection_id).exists():
                return Task.objects.none()
            return Task.objects.filter(collection=collection_id)

        return Task.objects.filter(collection__in=accessible_collections)

    def perform_create(self, serializer):
        collection = serializer.validated_data["collection"]
        user = self.request.user

        # Owner can always create tasks
        if collection.owner == user:
            serializer.save(owner=user, collection=collection)
            return

        # Check for edit permission through sharing
        if SharedPage.objects.filter(page=collection, shared_with=user, permission="edit").exists():
            serializer.save(owner=user, collection=collection)
            return

        # Check for link-based edit permission
        if collection.is_link_shareable and collection.shareable_permission == "edit":
            serializer.save(owner=user, collection=collection)
            return

        raise PermissionDenied("You don't have permission to create tasks here.")
