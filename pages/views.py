# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.db.models import Q
from pages.models import Collection
from sharing.models import SharedPage
from pages.serializers import CollectionShareSerializer, LinkShareSettingsSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer
from users.models import User
from rest_framework.exceptions import PermissionDenied
from notifications.models import Notification
from django.conf import settings


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retrieve only collections owned by the user
        user = self.request.user
        return Collection.objects.filter(owner=user, active=True).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.owner != request.user:
            raise PermissionDenied("You don't have permission to delete this collection")

        # Soft delete implementation
        instance.active = False
        instance.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SharedWithUserCollectionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Retrieve collections shared with the user
        user = self.request.user
        shared_collections = Collection.objects.filter(
            shared_entries__shared_with=user, active=True
        ).distinct()

        serializer = CollectionShareSerializer(shared_collections, many=True)
        return Response(serializer.data, status=200)


class SharePageWithUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        page_id = request.data.get("page_id")
        usernames = request.data.get("usernames", [])
        permission = request.data.get("permission")

        try:
            page = Collection.objects.get(id=page_id, owner=request.user, active=True)
        except Collection.DoesNotExist:
            return Response({"error": "Page not found or you are not the owner."}, status=404)

        shared_users = User.objects.filter(username__in=usernames).exclude(id=page.owner.id)
        created = []

        if page.is_link_shareable:
            page_url = f"{settings.FRONTEND_BASE_URL}/shared-page/{page.shareable_link_token}/"
        else:
            page_url = f"{settings.FRONTEND_BASE_URL}/collections/{page.id}/"

        for user in shared_users:
            shared_entry, created_flag = SharedPage.objects.update_or_create(
                page=page,
                shared_with=user,
                defaults={"permission": permission},
            )
            created.append(user.username)

            Notification.objects.create(
                recipient=user,
                sender=request.user,
                message=f"{request.user.username} has shared a page with you.",
                link=page_url,
            )

        return Response(
            {
                "shared_with": created,
                "permission": permission,
                "shared_page_url": page_url,
            },
            status=200,
        )


class PageByTokenView(RetrieveAPIView):
    serializer_class = CollectionShareSerializer
    lookup_field = "shareable_link_token"
    queryset = Collection.objects.filter(active=True)

    def get_object(self):
        obj = super().get_object()
        if not obj.is_link_shareable or not obj.active:
            raise PermissionDenied("This page is not available")
        return obj


class CollectionDetailWithTasks(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, collection_id):
        try:
            collection = (
                Collection.objects.filter(
                    Q(id=collection_id),
                    Q(owner=request.user) | Q(shared_entries__shared_with=request.user),
                    active=True,
                )
                .distinct()
                .get()
            )
        except Collection.DoesNotExist:
            return Response({"error": "Collection not found or no access."}, status=404)

        collection_data = CollectionShareSerializer(collection).data
        tasks = Task.objects.filter(collection=collection)
        tasks_data = TaskSerializer(tasks, many=True).data

        return Response({"collection": collection_data, "tasks": tasks_data}, status=200)


class UpdateLinkShareSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, page_id):
        try:
            page = Collection.objects.get(id=page_id, owner=request.user, active=True)
        except Collection.DoesNotExist:
            return Response({"error": "Page not found or not owned by you."}, status=404)

        serializer = LinkShareSettingsSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            link = f"{settings.FRONTEND_BASE_URL}/shared-page/{page.shareable_link_token}/"
            return Response(
                {
                    "message": "Share settings updated.",
                    "is_link_shareable": page.is_link_shareable,
                    "shareable_permission": page.shareable_permission,
                    "shareable_link_token": str(page.shareable_link_token),
                    "shareable_link_url": link,
                }
            )
        return Response(serializer.errors, status=400)


# views.py
class GetLinkShareSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, page_id):
        try:
            page = Collection.objects.get(id=page_id, owner=request.user, active=True)
        except Collection.DoesNotExist:
            return Response({"error": "Page not found or not owned by you."}, status=404)
        serializer = LinkShareSettingsSerializer(page)
        return Response(serializer.data)


class GetSharedUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, page_id):
        try:
            page = Collection.objects.get(id=page_id, owner=request.user, active=True)
        except Collection.DoesNotExist:
            return Response({"error": "Page not found or not owned by you."}, status=404)
        shared_users = SharedPage.objects.filter(page=page).values_list(
            "shared_with__username", flat=True
        )
        return Response({"shared_users": list(shared_users)})


class UnshareAllUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, page_id):
        try:
            page = Collection.objects.get(id=page_id, owner=request.user, active=True)
        except Collection.DoesNotExist:
            return Response({"error": "Page not found or not owned by you."}, status=404)
        SharedPage.objects.filter(page=page).delete()
        return Response({"message": "All shared users removed."}, status=200)
