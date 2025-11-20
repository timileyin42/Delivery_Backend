from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    LoginView,
    logout_view,
    UserProfileView,
    PasswordUpdateView,
    PasswordResetRequestView,
    UserListView,
    UserDetailView,
)
from .email_views import (
    verify_email_view,
    resend_verification_email_view,
    initiate_password_reset_view,
    confirm_password_reset_view,
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Email Verification
    path('verify-email/', verify_email_view, name='verify-email'),
    path('resend-verification/', resend_verification_email_view, name='resend-verification'),
    
    # Password Reset (Updated)
    path('password-update/', PasswordUpdateView.as_view(), name='password-update'),
    path('initiate-reset/', initiate_password_reset_view, name='initiate-reset'),
    path('confirm-reset/', confirm_password_reset_view, name='confirm-reset'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # User Management (Admin)
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
