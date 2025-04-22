from users.models import User, EmailVerificationToken, PasswordResetToken
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer
)
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse


# Create your views here.
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Create user but set as inactive until email is verified
            user = serializer.save()
            user.is_active = False
            user.save()
            
            # Create verification token
            token = EmailVerificationToken.objects.create(user=user)
            
            # Build verification link - use frontend verification route
            protocol = 'https' if request.is_secure() else 'http'
            frontend_domain = "localhost:5173"  # Change in production
            verification_url = f"{protocol}://{frontend_domain}/verify-email?token={token.token}"
            
            # Send verification email
            send_mail(
                'Activate your Life Tracker account',
                f'Hi {user.username},\n\nThank you for registering with Life Tracker! '
                f'Please click the link below to verify your email and activate your account:\n\n'
                f'{verification_url}\n\n'
                f'This link will expire in 24 hours.\n\n'
                f'If you did not create this account, please ignore this email.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return Response(
                {
                    "message": "User registered successfully. Please check your email to verify your account.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response(
                {"success": False, "error": "Verification token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification_token = get_object_or_404(EmailVerificationToken, token=token)
            
            # Check if token is expired
            if verification_token.expires_at < timezone.now():
                return Response(
                    {
                        "success": False,
                        "error": "Verification token has expired",
                        "email": verification_token.user.email
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Activate user
            user = verification_token.user
            user.is_active = True
            user.save()
            
            # Delete the used token
            verification_token.delete()
            
            # Generate tokens for auto-login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "success": True,
                "message": "Email verified successfully. Your account is now active.",
                "username": user.username,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            })
            
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendEmailVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email address is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            # Check if user is already active
            if user.is_active:
                return Response({"message": "Account is already verified."}, status=status.HTTP_200_OK)
            
            # Delete any existing tokens
            EmailVerificationToken.objects.filter(user=user).delete()
            
            # Create new verification token
            token = EmailVerificationToken.objects.create(user=user)
            
            # Build verification link - use frontend verification route
            protocol = 'https' if request.is_secure() else 'http'
            frontend_domain = "localhost:5173"  # Change in production
            verification_url = f"{protocol}://{frontend_domain}/verify-email?token={token.token}"
            
            # Send verification email
            send_mail(
                'Activate your Life Tracker account',
                f'Hi {user.username},\n\nYou have requested a new verification link. '
                f'Please click the link below to verify your email and activate your account:\n\n'
                f'{verification_url}\n\n'
                f'This link will expire in 24 hours.\n\n'
                f'If you did not request this email, please ignore it.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response(
                {"message": "Verification email has been sent. Please check your inbox."},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            # For security reasons, don't reveal if the email exists or not
            return Response(
                {"message": "If the email exists in our system, a verification link has been sent."},
                status=status.HTTP_200_OK
            )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            # First check if user exists without checking activation status
            try:
                user = User.objects.get(username=username)
                
                # If user exists but is not active, this is an unverified account
                if not user.is_active:
                    return Response(
                        {
                            "error": "Please verify your email before logging in.",
                            "verification_required": True,
                            "email": user.email
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Now try to authenticate (which checks password)
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user:
                    refresh = RefreshToken.for_user(authenticated_user)
                    return Response(
                        {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "user": UserSerializer(authenticated_user).data,
                        }
                    )
                else:
                    # User exists but password is wrong
                    return Response({"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
                    
            except User.DoesNotExist:
                # User doesn't exist
                return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.exclude(id=request.user.id).values_list("username", flat=True)
        return Response({"usernames": list(users)})


# New view for the API test page
def api_test_view(request):
    """View function to serve the API test HTML page"""
    return render(request, 'users/login_test.html')


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Delete any existing tokens
                PasswordResetToken.objects.filter(user=user).delete()
                
                # Create new token
                token = PasswordResetToken.objects.create(user=user)
                
                # Build reset link
                protocol = 'https' if request.is_secure() else 'http'
                frontend_domain = "localhost:5173"  # Change in production
                reset_url = f"{protocol}://{frontend_domain}/reset-password?token={token.token}"
                
                # Send password reset email
                send_mail(
                    'Reset your Life Tracker password',
                    f'Hi {user.username},\n\nWe received a request to reset your password. '
                    f'Please click the link below to set a new password:\n\n'
                    f'{reset_url}\n\n'
                    f'This link will expire in 1 hour.\n\n'
                    f'If you did not request a password reset, please ignore this email.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                return Response(
                    {"message": "If the email exists in our system, a password reset link has been sent."},
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                # For security reasons, don't reveal if the email exists or not
                return Response(
                    {"message": "If the email exists in our system, a password reset link has been sent."},
                    status=status.HTTP_200_OK
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token_str = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                token = get_object_or_404(PasswordResetToken, token=token_str)
                
                # Check if token is expired or already used
                if token.expires_at < timezone.now():
                    return Response(
                        {"error": "Password reset token has expired."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                if token.is_used:
                    return Response(
                        {"error": "This password reset link has already been used."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Reset the user's password
                user = token.user
                user.set_password(password)
                user.save()
                
                # Mark token as used
                token.is_used = True
                token.save()
                
                # Generate tokens for auto-login
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "message": "Password has been reset successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data,
                })
                
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check if current password is correct
            user = request.user
            current_password = serializer.validated_data['current_password']
            if not user.check_password(current_password):
                return Response(
                    {"error": "Current password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Generate new tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Password changed successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
