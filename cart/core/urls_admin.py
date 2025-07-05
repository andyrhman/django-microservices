from django.urls import path

from core.views import CartAdminListAPIView, CartsAdminRetriveAPIView, TotalCartsAPIView

urlpatterns = [
    path('', CartAdminListAPIView.as_view()),
    path('<str:id>', CartsAdminRetriveAPIView.as_view()), 
    path('total-carts', TotalCartsAPIView.as_view()), 
]