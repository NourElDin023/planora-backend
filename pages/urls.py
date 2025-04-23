from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pages.views import (
    CollectionDetailWithTasks,
    GetLinkShareSettingsView,
    GetSharedUsersView,
    PageViewSet,
    SharePageWithUsersView,
    PageByTokenView,
    UpdateLinkShareSettingsView,
    UnshareAllUsersView,
    SharedWithUserCollectionsView,
)

router = DefaultRouter()
router.register(r"", PageViewSet, basename="pages")

urlpatterns = [
    path("share/", SharePageWithUsersView.as_view(), name="share-page"),
    path(
        "token/<uuid:shareable_link_token>/",
        PageByTokenView.as_view(),
        name="page-by-token",
    ),
    path(
        "<int:page_id>/share-settings/",
        UpdateLinkShareSettingsView.as_view(),
        name="page-share-settings",
    ),
    path("shared-collections/", SharedWithUserCollectionsView.as_view(), name="shared-collections"),
    path("", include(router.urls)),
    path(
        "<int:collection_id>/tasks/", CollectionDetailWithTasks.as_view(), name="collection-tasks"
    ),
    path(
        "<int:page_id>/get-share-settings/",
        GetLinkShareSettingsView.as_view(),
        name="get-share-settings",
    ),
    path("<int:page_id>/shared-users/", GetSharedUsersView.as_view(), name="shared-users"),
    path("<int:page_id>/unshare-all/", UnshareAllUsersView.as_view(), name="unshare-all-users"),
]
