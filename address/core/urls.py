from django.urls import path

from core.views import AddressDetailAPIView

urlpatterns = [
    path("", AddressDetailAPIView.as_view(), name="address-crud"),
]