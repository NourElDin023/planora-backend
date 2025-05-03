from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import OutlookToken
import requests
import datetime
from django.http import JsonResponse
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response


OUTLOOK_CLIENT_ID = settings.OUTLOOK_CLIENT_ID

def outlook_login(request):
    if not request.user.is_authenticated:
        # print("OUTLOOK_CLIENT_ID =", os.getenv('OUTLOOK_CLIENT_ID'))

        scope = "offline_access Calendars.ReadWrite"
        auth_url = (
            f"https://login.microsoftonline.com/{settings.OUTLOOK_TENANT_ID}/oauth2/v2.0/authorize"
            f"?client_id={OUTLOOK_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={settings.OUTLOOK_REDIRECT_URI}"
            f"&response_mode=query"
            f"&scope={scope}"
        )
        return redirect(auth_url)

    return JsonResponse({"error": "User already logged in."})



@api_view(['POST'])
@permission_classes([IsAuthenticated])  # ensure user is logged in
def calendar_sync(request):
    access_token = request.data.get('accessToken')

    if not access_token:
        return Response({"error": "No access token provided"}, status=400)

    # Store or update Outlook token
    OutlookToken.objects.update_or_create(
        user=request.user,
        defaults={
            'access_token': access_token,
            'refresh_token': '',  # MSAL popup does not give refresh token
            'expires_at': timezone.now() + datetime.timedelta(hours=1)
        }
    )

    return Response({"message": "Access token saved successfully"})


@login_required
def get_calendar_events(request):
    try:
        token = OutlookToken.objects.get(user=request.user)
        headers = {
            'Authorization': f'Bearer {token.access_token}',
            'Accept': 'application/json',
        }
        graph_url = 'https://graph.microsoft.com/v1.0/me/events'
        response = requests.get(graph_url, headers=headers)
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({"error": "Failed to fetch events."}, status=400)
    except OutlookToken.DoesNotExist:
        return JsonResponse({"error": "No token found for this user."}, status=404)
