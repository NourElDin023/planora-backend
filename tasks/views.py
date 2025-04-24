from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Allow all actions while maintaining security
        queryset = Task.objects.filter(owner=self.request.user)

        # Apply collection filter only for list actions
        if self.action == "list":
            collection_id = self.request.query_params.get("collection")
            if collection_id:
                queryset = queryset.filter(collection=collection_id)

        return queryset.order_by("-due_date", "due_time")

    def perform_create(self, serializer):
        # Ensure collection is from validated data, not query params
        serializer.save(owner=self.request.user, collection=serializer.validated_data["collection"])
