from django.urls import path

from authorization.views import BulkUsersAPIView, HealthCheckAPIView, LoginAPIView, LogoutAPIView, RegisterAPIView, TotalUsersAPIView, UpdateInfoAPIView, UpdatePasswordAPIView, UserAPIView,UsersAPIView 

urlpatterns = [
    path("register", RegisterAPIView.as_view(), name='api-register'),
    path("login", LoginAPIView.as_view(), name='api-login'),
    path("", UserAPIView.as_view(), name='api-user'),
    path("users/bulk",  BulkUsersAPIView.as_view()),
    path("users", UsersAPIView.as_view()),
    path("users/<uuid:user_id>", UsersAPIView.as_view()),
    path("total-users", TotalUsersAPIView.as_view()),
    path("logout", LogoutAPIView.as_view(), name='api-logout'),
    path("info", UpdateInfoAPIView.as_view(), name='api-update-info'),
    path("password", UpdatePasswordAPIView.as_view(), name='api-update-password'),
    path("health", HealthCheckAPIView.as_view(), name='api-health-check'),
]
