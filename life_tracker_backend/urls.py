from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("tracker.urls")),
    path("api/users/", include("users.urls")),
    path("api/pages/", include("pages.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/tasks/", include("tasks.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
