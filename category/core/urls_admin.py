from django.urls import path

from core.views import CategoryGenericAPIView

urlpatterns = [
    path("category", CategoryGenericAPIView.as_view()),
    path("category/<str:id>", CategoryGenericAPIView.as_view()),
]
