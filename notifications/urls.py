from django.urls import path
from .views import UserNotificationsView

urlpatterns = [
    path("my/", UserNotificationsView.as_view(), name="user-notifications"),
]
