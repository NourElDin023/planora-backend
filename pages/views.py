from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.db.models import Q
from pages.models import Page
from sharing.models import SharedPage
from pages.serializers import PageShareSerializer, LinkShareSettingsSerializer
from users.models import User
from rest_framework.exceptions import PermissionDenied
from notifications.models import Notification
from django.urls import reverse


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Page.objects.filter(Q(owner=user) | Q(shared_entries__shared_with=user)).distinct()


class SharePageWithUsersView(APIView):
    """
    POST {
        "page_id": 1,
        "usernames": ["user1", "user2"],
        "permission": "edit"  # or "view"
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        page_id = request.data.get("page_id")
        usernames = request.data.get("usernames", [])
        permission = request.data.get("permission")

        try:
            page = Page.objects.get(id=page_id, owner=request.user)
        except Page.DoesNotExist:
            return Response({"error": "Page not found or you are not the owner."}, status=404)

        shared_users = User.objects.filter(username__in=usernames).exclude(id=page.owner.id)
        created = []

        # Build the page link (based on shareable or not)
        if page.is_link_shareable:
            page_url = request.build_absolute_uri(
                reverse("page-by-token", args=[str(page.shareable_link_token)])
            )
        else:
            page_url = request.build_absolute_uri(reverse("pages-detail", args=[page.id]))

        for user in shared_users:
            shared_entry, created_flag = SharedPage.objects.update_or_create(
                page=page,
                shared_with=user,
                defaults={"permission": permission},
            )
            created.append(user.username)

            # ✅ Send a notification
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
    """
    Anyone with the link can access the page if sharing is enabled.
    """

    serializer_class = PageShareSerializer
    lookup_field = "shareable_link_token"
    queryset = Page.objects.all()

    def get_object(self):
        obj = super().get_object()
        if not obj.is_link_shareable:
            raise PermissionDenied("This page is not publicly shareable.")
        return obj


class UpdateLinkShareSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, page_id):
        try:
            page = Page.objects.get(id=page_id, owner=request.user)
        except Page.DoesNotExist:
            return Response({"error": "Page not found or not owned by you."}, status=404)

        serializer = LinkShareSettingsSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            link = request.build_absolute_uri(f"/api/pages/token/{page.shareable_link_token}/")
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
