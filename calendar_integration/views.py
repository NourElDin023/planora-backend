import os
import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from dotenv import load_dotenv
from django.conf import settings
from .models import CalendarToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
load_dotenv()

def get_auth_url(request):
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI")
    scopes = "offline_access user.read calendars.readwrite"

    auth_url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&response_mode=query"
        f"&scope={scopes}"
    )

    return redirect(auth_url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_callback(request):
    print("User in callback:", request.user)

    # if not request.user.is_authenticated:
    #     return JsonResponse({'error': 'Authentication required'}, status=401)

    code = request.GET.get("code")

    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    redirect_uri = os.getenv("MICROSOFT_REDIRECT_URI")
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

    data = {
        "client_id": client_id,
        "scope": "offline_access user.read calendars.readwrite",
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "client_secret": client_secret,
    }

    response = requests.post(token_url, data=data)

    if response.status_code != 200:
        return JsonResponse({"error": "Token request failed", "details": response.json()}, status=400)

    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 3600)
    token_type = token_data.get("token_type", "Bearer")

    # Store or update the user's calendar tokens in the database
    user = request.user  # Get the logged-in user
    CalendarToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "token_type": token_type,
        }
    )

    return JsonResponse({
        "message": "Authorization successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    })


@csrf_exempt  # Disable CSRF for this API endpoint (not recommended for production without additional security)
def calendar_sync(request):
    if request.method == 'POST':
        access_token = request.headers.get('Authorization')

        if not access_token:
            return JsonResponse({"error": "Access token is missing"}, status=400)

        token = access_token.split(" ")[1] if access_token.startswith("Bearer ") else access_token

        calendar_url = "https://graph.microsoft.com/v1.0/me/events"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        response = requests.get(calendar_url, headers=headers)

        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({"error": response.json()}, status=response.status_code)

    return JsonResponse({"error": "Invalid method. Use POST."}, status=405)
