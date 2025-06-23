import jwt
from django.conf import settings
from rest_framework import permissions
from decouple import config

class IsAdminScope(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.COOKIES.get("user_session")
        if not token:
            return False
        try:
            payload = jwt.decode(
                token,
                config("JWT_SECRET"),
                algorithms=["HS256"]
            )
        except jwt.PyJWTError:
            return False

        return payload.get("scope") == "admin"
