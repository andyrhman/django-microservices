from django.urls import path

from core.views import CartAdminListAPIView, CartsAdminRetriveAPIView, TotalCartsAPIView

urlpatterns = [
    path('carts', CartAdminListAPIView.as_view()),
    path('carts/<str:id>', CartsAdminRetriveAPIView.as_view()), 
    path('total-carts', TotalCartsAPIView.as_view()), 
]