from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pages.views import (
    CollectionDetailWithTasks,
    PageViewSet,
    SharePageWithUsersView,
    PageByTokenView,
    UpdateLinkShareSettingsView,
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
    path("", include(router.urls)),
    path(
        "<int:collection_id>/tasks/", CollectionDetailWithTasks.as_view(), name="collection-tasks"
    ),
]
