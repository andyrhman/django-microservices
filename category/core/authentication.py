import jwt, datetime
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from decouple import config

class ServiceUser:
    def __init__(self, user_id, scope):
        self.id     = user_id
        self.scope  = scope

    @property
    def is_authenticated(self):
        return True

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('user_session')
        if not token:
            return None

        try:
            payload = jwt.decode(token,
                                 config('JWT_SECRET'),
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expired')
        except jwt.PyJWTError:
            raise exceptions.AuthenticationFailed('Invalid token')

        scope = payload.get('scope')
        path  = request.path.lower()

        # enforce that the JWT’s scope matches the endpoint
        if path.startswith('/api/admin/') and scope != 'admin':
            raise exceptions.AuthenticationFailed('Admin only')
        if path.startswith('/api/user/')  and scope != 'user':
            raise exceptions.AuthenticationFailed('User only')
        if path.startswith('/api/') and scope not in ('user','admin'):
            raise exceptions.AuthenticationFailed('Invalid scope')

        user = ServiceUser(payload['user_id'], scope)
        return (user, None)

    def authenticate_header(self, request):
        return 'Bearer'
