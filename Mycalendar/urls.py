from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.outlook_login, name='outlook-login'),
    path('sync/', views.calendar_sync, name='outlook-sync'),
    path('events/', views.get_calendar_events, name='get_calendar_events'),

]
