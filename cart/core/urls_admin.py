from django.urls import path

from core.views import CartAdminListAPIView, CartsAdminRetriveAPIView, TotalCartsAPIView

urlpatterns = [
    path('carts/cart', CartAdminListAPIView.as_view()),
    path('carts/cart/<str:id>', CartsAdminRetriveAPIView.as_view()), 
    path('carts/cart/total-carts/', TotalCartsAPIView.as_view()), 
]