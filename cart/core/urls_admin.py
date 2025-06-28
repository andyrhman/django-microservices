from django.urls import path

from core.views import CartAdminListAPIView, CartBulkAPIView, CartsAdminRetriveAPIView

urlpatterns = [
    path('carts', CartAdminListAPIView.as_view()),
    path('carts/<str:id>', CartsAdminRetriveAPIView.as_view()), 
]