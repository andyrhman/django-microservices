from django.urls import path

from core.views import CartBulkAPICompletedView, CartBulkAPIView, CartCRUDAPIView, TotalCartAPIView, UserCartCompleteAPIView

urlpatterns = [
    path('cart', CartCRUDAPIView.as_view(), name='api-cart'),
    path('cart/<str:id>', CartCRUDAPIView.as_view(), name='api-cart-detail'),
    path('cart-total', TotalCartAPIView.as_view(), name='api-cart-total'),
    path('carts/bulk/completed', CartBulkAPICompletedView.as_view(), name='admin-cart-bulk'), 
    path('carts/bulk', CartBulkAPIView.as_view(), name='admin-cart-bulk'), 
    path('carts/<uuid:id>/complete', UserCartCompleteAPIView.as_view(), name='cart-complete'),   
]