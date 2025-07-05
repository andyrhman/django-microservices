from django.urls import path
from core.views import AddressAPIView

urlpatterns = [
    path("", AddressAPIView.as_view()),
    path("<uuid:id>", AddressAPIView.as_view()),
]