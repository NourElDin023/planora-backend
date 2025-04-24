from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pages.views import (
    PageViewSet,
    SharePageWithUsersView,
    PageByTokenView,
    UpdateLinkShareSettingsView,
    summarize_note,
)

router = DefaultRouter()
router.register(r"", PageViewSet, basename="pages")

urlpatterns = [
    path("summarize/", summarize_note, name='summarize-note'),
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
]
