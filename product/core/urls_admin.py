from django.urls import path

from core.views import ProductImagesCDAPIView, ProductListCreateAPIView, ProductRUDAPIView, ProductVariantCDAPIView, TotalProductsAPIView


urlpatterns = [
    path('', ProductListCreateAPIView.as_view()),
    path('<str:id>', ProductRUDAPIView.as_view()),
    path('product-variants', ProductVariantCDAPIView.as_view()),
    path('product-variants/<str:id>', ProductVariantCDAPIView.as_view()),
    path('product-images', ProductImagesCDAPIView.as_view()),
    path('product-images/<str:id>', ProductImagesCDAPIView.as_view()),
    path('total-products', TotalProductsAPIView.as_view()),
]