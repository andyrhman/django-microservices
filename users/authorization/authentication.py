import jwt, datetime
from decouple import config
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from core.models import User, UserSession

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('user_session')
        if not token:
            return None

        try:
            payload = jwt.decode(token, config('JWT_SECRET'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Unauthenticated')

        path = request.path.lower()
        if path.startswith('/api/admin/'):
            if payload['scope'] != 'admin':
                raise exceptions.AuthenticationFailed('Invalid Scope!')
        elif path.startswith('/api/user/'):
            if payload['scope'] != 'user':
                raise exceptions.AuthenticationFailed('Invalid Scope!')
        elif path.startswith('/api/'):
            if payload['scope'] not in ('user', 'admin'):
                raise exceptions.AuthenticationFailed('Invalid Scope!')
        else:
            return None

        user = User.objects.get(id=payload['user_id'])
        
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')
        
        if not UserSession.objects.filter(user=user.id, token=token, expired_at__gt=datetime.datetime.now(datetime.timezone.utc)).exists():
            raise exceptions.AuthenticationFailed('Unauthenticated')
        
        return (user, None)
    
    @staticmethod
    def generate_jwt(user_id, scope):
        now = datetime.datetime.now(datetime.timezone.utc)
        exp = now + datetime.timedelta(days=1)
        payload = {
            'user_id': str(user_id),
            'scope': scope,
            'iat': now,
            'exp': exp,
        }
        token = jwt.encode(payload, config('JWT_SECRET'), algorithm='HS256')
        return token, exp