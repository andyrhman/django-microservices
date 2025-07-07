from django.urls import path

from core.views import CategoryGenericAPIView

urlpatterns = [
    path("categories/category", CategoryGenericAPIView.as_view()),
    path("categories/category/<str:id>", CategoryGenericAPIView.as_view()),
]
