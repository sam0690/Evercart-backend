from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status, generics
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, UserSerializer, AdminUserSerializer


def _is_admin(user):
    return (
        getattr(user, "is_staff", False)
        or getattr(user, "is_superuser", False)
        or getattr(user, "is_admin", False)
    )

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

# login: uses built-in TokenObtainPairView but we set cookie
class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        # resp is a DRF Response with data {'refresh':..., 'access':...}
        if resp.status_code == 200 and "refresh" in resp.data:
            refresh = resp.data.get("refresh")
            access = resp.data.get("access")
            
            # Get user data
            from rest_framework_simplejwt.tokens import AccessToken
            token = AccessToken(access)
            user_id = token['user_id']
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                user_data = UserSerializer(user).data
            except User.DoesNotExist:
                user_data = None
            
            # Return both tokens and user data in JSON
            response = JsonResponse({
                "access": access,
                "refresh": refresh,  # Include refresh in response for localStorage
                "user": user_data
            })
            
            # Also set refresh token as HttpOnly cookie for additional security
            response.set_cookie(
                "refresh",
                refresh,
                httponly=True,
                samesite="Lax",
                secure=False,    # set True in production over HTTPS
                max_age=7*24*3600,
            )
            return response
        return JsonResponse(resp.data, status=resp.status_code)

@method_decorator(csrf_exempt, name="dispatch")
class AdminLoginView(TokenObtainPairView):
    """Admin-only login endpoint. Returns tokens only for admin/staff/superuser."""
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if resp.status_code != 200 or "access" not in resp.data:
            return JsonResponse(resp.data, status=resp.status_code)

        access = resp.data.get("access")
        refresh = resp.data.get("refresh")

        # Decode access to find user
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(access)
        user_id = token["user_id"]

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"detail": "Invalid user"}, status=400)

        is_admin = getattr(user, "is_staff", False) or getattr(user, "is_superuser", False) or getattr(user, "is_admin", False)
        if not is_admin:
            return JsonResponse({"detail": "Admin access only"}, status=403)

        # OK: return same structure as LoginView with user and cookie
        # Plus simple keys to match simplified flow (message, is_admin)
        user_data = UserSerializer(user).data
        response = JsonResponse({
            "access": access,
            "refresh": refresh,
            "user": user_data,
            "message": "Login successful",
            "is_admin": True,
        })
        response.set_cookie(
            "refresh",
            refresh,
            httponly=True,
            samesite="Lax",
            secure=False,  # set True behind HTTPS in production
            max_age=7*24*3600,
        )
        return response

@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_access_token(request):
    """
    Issue a new access token from a refresh token.
    Accepts refresh token from HttpOnly cookie 'refresh' or JSON body {"refresh": "..."}.
    """
    refresh_token = request.COOKIES.get("refresh") or request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "No refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        token = RefreshToken(refresh_token)
        access = str(token.access_token)
        return Response({"access": access})
    except Exception:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    response = JsonResponse({"message": "Logged out"})
    response.delete_cookie("refresh")
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# =====================
# Admin-only API Views
# =====================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_profile_view(request):
    """Admin-only: Get current admin's profile (requires admin role)"""
    user = request.user
    if not _is_admin(user):
        return Response({"detail": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def list_users(request):
    """Admin-only: list or create users"""
    user = request.user
    if not _is_admin(user):
        return Response({"detail": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)

    User = get_user_model()
    if request.method == "GET":
        queryset = User.objects.all().order_by("-date_joined")
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    serializer = AdminUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user_instance = serializer.save()
    return Response(AdminUserSerializer(user_instance).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def admin_user_detail(request, user_id: int):
    """Admin-only: retrieve, update, or delete a specific user"""
    if not _is_admin(request.user):
        return Response({"detail": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)

    User = get_user_model()
    try:
        user_instance = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = AdminUserSerializer(user_instance)
        return Response(serializer.data)

    if request.method == "PATCH":
        serializer = AdminUserSerializer(user_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminUserSerializer(user_instance).data)

    if user_instance.id == request.user.id:
        return Response({"detail": "You cannot delete your own account"}, status=status.HTTP_400_BAD_REQUEST)

    user_instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["POST"])
@permission_classes([AllowAny])
def admin_refresh_access_token(request):
    """
    Admin-only: Issue a new access token from a refresh token.
    Validates that the user is an admin before issuing the new token.
    Accepts refresh token from HttpOnly cookie 'refresh' or JSON body {"refresh": "..."}.
    """
    refresh_token = request.COOKIES.get("refresh") or request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "No refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        token = RefreshToken(refresh_token)
        # Extract user_id to validate admin role
        user_id = token.payload.get("user_id")
        if not user_id:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verify admin role
        if not _is_admin(user):
            return Response({"detail": "Admin access only"}, status=status.HTTP_403_FORBIDDEN)
        
        access = str(token.access_token)
        return Response({"access": access})
    except Exception:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
