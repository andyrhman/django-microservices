from django.urls import path

from authorization.views import ResendVerifyAPIView, UsersAPIView, VerifyAccountAPIView

urlpatterns = [
    path("", ResendVerifyAPIView.as_view(), name='api-resend-verify'),
    path("<str:token>", VerifyAccountAPIView.as_view(), name='api-verify-account'),
]