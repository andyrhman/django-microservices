import jwt
from django.utils.deprecation import MiddlewareMixin
from rest_framework import exceptions
from decouple import config

def _detect_scope_from_path(path: str) -> str:
    return 'admin' if path.lower().startswith('/api/admin/') else 'user'

class UserMicroserviceAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.user_ms = None
        token = request.COOKIES.get('user_session')
        if not token:
            return

        try:
            payload = jwt.decode(token, config("JWT_SECRET"), algorithms=['HS256'])
        except jwt.PyJWTError:
            return exceptions.JsonResponse(
                {"message": "Unauthenticated"},
                status=401
            )

        desired = _detect_scope_from_path(request.path)
        if payload.get('scope') != desired:
            return exceptions.JsonResponse(
                {"message": "Invalid Scope!"},
                status=403
            )

        request.user_ms = payload.get('user_id')