from django.urls import path

from core.views import AddressDetailAPIView, HealthCheckAPIView

urlpatterns = [
    path("address", AddressDetailAPIView.as_view(), name="address-crud"),
    path("address/health", HealthCheckAPIView.as_view(), name="address-crud"),
]