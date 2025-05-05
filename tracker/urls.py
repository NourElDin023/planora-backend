from django.urls import path
from .views import notes_list, note_detail

urlpatterns = [
    path("notes/", notes_list, name="notes-list"),
    path("notes/<int:pk>/", note_detail, name="note-detail"),
]
