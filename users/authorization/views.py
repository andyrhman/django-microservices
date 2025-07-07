from codecs import lookup
import datetime
import secrets
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.views.generic import TemplateView
from rest_framework import exceptions, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.authentication import JWTAuthentication
from authorization.serializers import UserSerializer
from core.models import Token, User, UserSession
from decouple import config
from django.views.generic import TemplateView
from app.producer import send_message
from core.utils import detect_scope_from_path
from authorization.permissions import IsAdminScope

# Create your views here.
class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data["password"] != data["confirm_password"]:
            raise exceptions.APIException("Password do not match!")

        serializer = UserSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': "Successfully Registered"})

class LoginAPIView(APIView):

    def post(self, request):
        data  = request.data
        scope = detect_scope_from_path(request.path)

        # 1) Lookup by email or username
        if "email" in data:
            lookup = {"email": data["email"].lower()}
        elif "username" in data:
            lookup = {"username": data["username"].lower()}
        else:
            return Response(
                {"message": "Must supply email or username"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(**lookup)
        except ObjectDoesNotExist:
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2) Password check
        if not user.check_password(data.get("password", "")):
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3) Verified?
        if not user.is_verified:
            return Response(
                {"message": "Please verify your account first"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 4) User trying to login via admin endpoint?
        if user.is_user and scope == "admin":
            raise exceptions.AuthenticationFailed("Unauthorized")

        # 5) Generate & save JWT
        token, exp = JWTAuthentication.generate_jwt(user.id, scope)
        UserSession.objects.create(
            user       = user.id,
            token      = token,
            expired_at = exp
        )

        # 6) Return to client
        resp = Response({"jwt": token}, status=status.HTTP_200_OK)
        resp.set_cookie(
            key      = "user_session",
            value    = token,
            httponly = True,
        )
        return resp


class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        serializer = UserSerializer(user)

        return Response(serializer.data)

class UsersAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAdminScope]
    lookup_field = "user_id"

    def get(self, request, user_id=None):
        is_admin = getattr(request, "scope", None) == "admin"

        if not is_admin:
            return Response(
                {"message": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
                   
        if user_id is None:
            qs = User.objects.all()
            s = request.query_params.get("search", "")
            if s:
                qs = list(
                    [
                        u
                        for u in qs
                        if (s.lower() in u.fullName.lower())
                        or (s.lower() in u.username.lower())
                    ]
                )           
            data = UserSerializer(qs, many=True).data
            return Response(data, status=status.HTTP_200_OK)

        user = User.objects.get(id=user_id)
        return Response(UserSerializer(user).data)

class BulkUsersAPIView(APIView):
    authentication_classes = []
    permission_classes     = [IsAdminScope]

    def post(self, request):
        ids = request.data.get("ids", [])
        if not isinstance(ids, list):
            return Response(
                {"message": "ids must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        users = User.objects.filter(id__in=ids)

        is_admin = getattr(request, "scope", None) == "admin"

        if is_admin:
            serialized = UserSerializer(users, many=True).data
        else:
            serialized = [
                {"id": str(u.id), "username": u.username}
                for u in users
            ]

        result = {u["id"]: u for u in serialized}
        return Response(result, status=status.HTTP_200_OK)
    
class TotalUsersAPIView(APIView):
    authentication_classes = []
    permission_classes = [IsAdminScope]
    
    def get(self, request):
        is_admin = getattr(request, "scope", None) == "admin"

        if not is_admin:
            return Response(
                {"message": "Unauthorized"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        users = User.objects.all()
        
        total = len(users)
        
        return Response({"total": total})
    
class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.COOKIES.get('user_session')
        UserSession.objects.filter(
            user=request.user.id,
            token=token
        ).delete()
        return Response({"message": "Success"})


class UpdateInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        try:
            data = request.data
            user = request.user
            serializer = UserSerializer(
                user,
                data={
                    "fullName": data.get("fullName", user.fullName),
                    "email": data.get("email", user.email),
                    "username": data.get("username", user.username),
                },
                context={"request": request},
                partial=True,
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except exceptions.ValidationError as e:
            if isinstance(e.detail, dict):
                errors = {key: value[0] for key, value in e.detail.items()}
                first_field = next(iter(errors))
                field_name = first_field.replace("_", " ").capitalize()
                if "already exists" in errors[first_field]:
                    message = f"{field_name} already exists."
                else:
                    message = f"{field_name} error: {errors[first_field]}"
            else:
                message = str(e.detail)
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        data = request.data
        user = request.user
        
        if data['password'] != data['confirm_password']:
            raise exceptions.APIException('Password do not match')

        user.set_password(data["password"])
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
            
class ResendVerifyAPIView(APIView):
    def post(self, request):
        data = request.data
        
        if not data['email']:
            raise exceptions.APIException("Provide your email address")

        user = User.objects.filter(email=data['email']).first()
        
        if not user:
            raise exceptions.APIException("Email not found")
        
        if user.is_verified:
            raise exceptions.APIException("Your account has already been verified")
        
        token_str = secrets.token_hex(16)
        expiresAt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)

        Token.objects.create(
            token=token_str,
            email=user.email,
            user=user,
            expiresAt=expiresAt ,
            used=False,
        )
        
        origin = config('ORIGIN')
        verify_url = f"{origin}/verify/{token_str}"

        payload = {
            "event": "user_registered",
            "user": model_to_dict(user),
            "verify_url": verify_url,
        }
        send_message(config('KAFKA_TOPIC', default='default'), payload)

        return Response(
            {"message": "Email has been sent successfully"},
            status=status.HTTP_200_OK,
        ) 


class VerifyAccountAPIView(APIView):
   
    def put(self, _, token=''):
        user_token = Token.objects.filter(token=token).first()
        
        if not user_token or user_token.expiresAt < datetime.datetime.now(datetime.timezone.utc) :
            return Response({'message': 'Token is invalid or expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user_token:
            return Response({'message': 'Invalid verify ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user_token.used:
            return Response({'message': 'Verify ID has already been used'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=user_token.email, pk=user_token.user.id).first()
        
        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        elif user.is_verified:
            return Response({'message': 'Your account has already been verified'}, status=status.HTTP_400_BAD_REQUEST)
        elif user.email != user_token.email and user.id != user_token.user:
            return Response({'message': 'Invalid Verify ID or email'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_token.used = True
        user_token.save()
        user.is_verified = True
        user.save()
        
        return Response({"message": "Account Verified Successfully"}, status=status.HTTP_202_ACCEPTED)
    
class HealthCheckAPIView(ListAPIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {"status": "✅ ok", "message": "🏃‍♀️‍➡️ service is running"},
            status=status.HTTP_200_OK
        )
        
class RegisterPageView(TemplateView):
    template_name = "auth/register.html"

class LoginPageView(TemplateView):
    template_name = "auth/login.html"

class VerifyPageView(TemplateView):
    template_name = "auth/verify.html"