from django.urls import path
from .views import chat_with_assistant

urlpatterns = [
    path("", chat_with_assistant, name="chat_view"),
]
