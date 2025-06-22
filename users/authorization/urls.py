from django.urls import path

from authorization.views import LoginAPIView, LogoutAPIView, RegisterAPIView, UpdateInfoAPIView, UpdatePasswordAPIView, UserAPIView, UserDetailByIdAPIView 

urlpatterns = [
    path("register", RegisterAPIView.as_view(), name='api-register'),
    path("login", LoginAPIView.as_view(), name='api-login'),
    path("", UserAPIView.as_view(), name='api-user'),
    path("<uuid:user_id>", UserDetailByIdAPIView.as_view()),
    path("logout", LogoutAPIView.as_view(), name='api-logout'),
    path("info", UpdateInfoAPIView.as_view(), name='api-update-info'),
    path("password", UpdatePasswordAPIView.as_view(), name='api-update-password'),
]
