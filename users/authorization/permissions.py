import jwt
from django.conf import settings
from rest_framework import permissions
from decouple import config

class IsAdminScope(permissions.BasePermission):
    def has_permission(self, request, view):
        token = request.COOKIES.get("user_session")
        request.scope = None
        if not token:
            return True
        try:
            payload = jwt.decode(
                token,
                config("JWT_SECRET"),
                algorithms=["HS256"]
            )
        except jwt.PyJWTError:
            return False
        request.scope = payload.get("scope")
        return True
