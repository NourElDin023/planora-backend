# notifications/urls.py
from django.urls import path
from .views import MarkNotificationsAsReadView, UnreadNotificationCountView, UserNotificationsView

urlpatterns = [
    path("my/", UserNotificationsView.as_view(), name="user-notifications"),
    path("unread_count/", UnreadNotificationCountView.as_view()),
    path("mark_as_read/", MarkNotificationsAsReadView.as_view()),
]
