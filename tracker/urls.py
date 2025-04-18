from django.urls import path
from .views import hello,notes_list, note_detail

urlpatterns = [
    path('notes/', notes_list),
    path('notes/<int:pk>/', note_detail),
    path('hello/', hello),  # Add this line
]
