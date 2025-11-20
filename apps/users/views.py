from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout

from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    UserProfileSerializer,
    PasswordUpdateSerializer,
    PasswordResetRequestSerializer
)
from .permissions import IsAdmin, IsAdminOrManager
from apps.common.utils import success_response, error_response
from apps.common.helpers import get_client_ip


class UserRegistrationView(generics.CreateAPIView):
    """
    Create new user (Admin only).
    POST /api/users/register/
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdmin]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create verification token and send email
        from apps.common.models import EmailVerificationToken
        from apps.common.email_service import EmailService
        
        token = EmailVerificationToken.objects.create(user=user)
        EmailService.send_verification_email(user, token.token)
        
        return Response(
            success_response(
                data=UserSerializer(user).data,
                message="User created successfully. Verification email sent."
            ),
            status=status.HTTP_201_CREATED
        )


class LoginView(generics.GenericAPIView):
    """
    User login with JWT tokens.
    POST /api/users/login/
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last login IP
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response(
            success_response(
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                },
                message="Login successful"
            ),
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout (blacklist refresh token).
    POST /api/users/logout/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        
        return Response(
            success_response(message="Logout successful"),
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get and update user profile.
    GET/PATCH /api/users/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(
            success_response(
                data=serializer.data,
                message="Profile retrieved successfully"
            ),
            status=status.HTTP_200_OK
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            success_response(
                data=serializer.data,
                message="Profile updated successfully"
            ),
            status=status.HTTP_200_OK
        )


class PasswordUpdateView(generics.GenericAPIView):
    """
    Update user password.
    POST /api/users/password-update/
    """
    serializer_class = PasswordUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            success_response(message="Password updated successfully"),
            status=status.HTTP_200_OK
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request password reset (send reset link).
    POST /api/users/password-reset/
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Send password reset email
        # For now, just return success
        
        return Response(
            success_response(
                message="Password reset instructions sent to your email"
            ),
            status=status.HTTP_200_OK
        )


class UserListView(generics.ListAPIView):
    """
    List all users (Admin/Manager only).
    GET /api/users/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    queryset = User.objects.all()
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['created_at', 'email']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success_response(
                data=serializer.data,
                message="Users retrieved successfully"
            )
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete specific user (Admin only).
    GET/PATCH/DELETE /api/users/{id}/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(
            success_response(
                data=serializer.data,
                message="User retrieved successfully"
            )
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            success_response(
                data=serializer.data,
                message="User updated successfully"
            )
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return Response(
            success_response(message="User deleted successfully"),
            status=status.HTTP_200_OK
        )
