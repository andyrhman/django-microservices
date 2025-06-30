from django.urls import path

from core.views import ChangeOrderStatus, GetOrderItem, OrderListAPIView, TotalOrderItemsAPIView, TotalOrdersAPIView

urlpatterns = [
    path('orders', OrderListAPIView.as_view()),
    path('order-items/<str:id>', GetOrderItem.as_view()),
    path('orders/<str:id>', ChangeOrderStatus.as_view()),
    path('total-orders', TotalOrdersAPIView.as_view()),
    path('total-orderitems', TotalOrderItemsAPIView.as_view())
]