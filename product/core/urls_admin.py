from django.urls import path

from core.views import ProductImagesCDAPIView, ProductListCreateAPIView, ProductRUDAPIView, ProductVariantCDAPIView, TotalProductsAPIView


urlpatterns = [
    path('products', ProductListCreateAPIView.as_view()),
    path('products/<str:id>', ProductRUDAPIView.as_view()),
    path('products/product-variants', ProductVariantCDAPIView.as_view()),
    path('products/product-variants/<str:id>', ProductVariantCDAPIView.as_view()),
    path('products/product-images', ProductImagesCDAPIView.as_view()),
    path('products/product-images/<str:id>', ProductImagesCDAPIView.as_view()),
    path('products/total-products/', TotalProductsAPIView.as_view()),
]