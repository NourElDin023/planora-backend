from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView, UserListView, api_test_view, 
    EmailVerificationView, ResendEmailVerificationView, PasswordResetRequestView,
    PasswordResetConfirmView, ChangePasswordView, AccountManagementView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("all-usernames/", UserListView.as_view(), name="all-usernames"),
    path("verify-email/", EmailVerificationView.as_view(), name="email-verify"),
    path("resend-verification/", ResendEmailVerificationView.as_view(), name="resend-verify"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    # Change account URL to match frontend expectations
    path("account/", AccountManagementView.as_view(), name="account-management"),
    path("deactivate-account/", AccountManagementView.as_view(), {"action": "deactivate"}, name="deactivate-account"),
    path("delete-account/", AccountManagementView.as_view(), {"action": "delete"}, name="delete-account"),
]
