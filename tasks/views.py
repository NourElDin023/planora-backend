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
        # Only include collections that are:
        # 1. Owned by the user
        # 2. Explicitly shared with the user via SharedPage
        # 3. Don't include link-shareable collections by default - they should only be accessible after visiting the shared link
        accessible_collections = Collection.objects.filter(
            Q(owner=user)
            | Q(shared_entries__shared_with=user)
        ).distinct()

        # Filter tasks based on collection access and optional collection filter
        collection_id = self.request.query_params.get("collection")
        if collection_id:
            # For specific collection requests, check if it's a link-shareable collection separately
            # This allows direct API calls to still work when needed
            collection = Collection.objects.filter(id=collection_id).first()
            if collection and (
                collection.owner == user 
                or SharedPage.objects.filter(page=collection, shared_with=user).exists()
                or (collection_id and collection.is_link_shareable and collection.shareable_permission in ["view", "edit"])
            ):
                return Task.objects.filter(collection=collection_id)
            return Task.objects.none()

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

        raise PermissionDenied("You don't have permission to create tasks here.")
