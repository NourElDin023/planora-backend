from django.urls import path
from . import views

urlpatterns = [
    path('authorize/', views.get_auth_url, name='calendar_authorize'),
    path('callback/', views.auth_callback, name='calendar_callback'),
    path('calendar-sync/', views.calendar_sync, name='calendar-sync'),

]
