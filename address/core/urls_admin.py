from django.urls import path
from core.views import AddressAPIView

urlpatterns = [
    path("address", AddressAPIView.as_view()),
    path("address/<uuid:id>", AddressAPIView.as_view()),
]