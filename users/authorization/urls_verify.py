from django.urls import path

from authorization.views import ResendVerifyAPIView, UserDetailByIdAPIView, VerifyAccountAPIView

urlpatterns = [
    path("verify", ResendVerifyAPIView.as_view(), name='api-resend-verify'),
    path("verify/<str:token>", VerifyAccountAPIView.as_view(), name='api-verify-account'),
    # path("api/user/<uuid:user_id>",  UserDetailByIdAPIView.as_view()),
    # path("api/admin/<uuid:user_id>", UserDetailByIdAPIView.as_view()),
]