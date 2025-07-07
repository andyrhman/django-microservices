
from django.contrib.messages import api
from django.urls import path

from core.views import ConfirmOrderGenericAPIView, CreateOrderAPIView, GetUserOrder, HealthCheckAPIView

urlpatterns = [
    path('orders/checkout/orders', CreateOrderAPIView.as_view(), name='api-create-order'),
    path('orders/checkout/orders/confirm', ConfirmOrderGenericAPIView.as_view(), name='api-confirm-order'),
    path('orders/order-user', GetUserOrder.as_view(), name='api-get-user-order'),
    path('orders/health', HealthCheckAPIView.as_view(), name='api-health-check'),
]