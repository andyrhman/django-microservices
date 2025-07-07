
from django.urls import path

from core.views import HealthCheckAPIView, ProductAPIView, ProductAvgRatingAPIView, ProductCategoryCountAPIView, ProductIdAPIView, ProductPriceFilterAPIView, ProductVariantsAPIView, ProductsAPIView


urlpatterns = [
    path('products/', ProductsAPIView.as_view(), name='api-products'),
    path('products/product/<str:slug>/', ProductAPIView.as_view(), name='api-product-detail'),
    path('products/product-id/<str:id>', ProductIdAPIView.as_view(), name='api-product-detail-id'),
    path('products/product/rating/<str:id>', ProductAvgRatingAPIView.as_view()),
    path('products/variants', ProductVariantsAPIView.as_view()),
    path("products/filter-by-price", ProductPriceFilterAPIView.as_view(), name="filter-by-price"),   
    path('products/product-category-counts', ProductCategoryCountAPIView.as_view(), name='api-product-category-counts'),
    path('products/health', HealthCheckAPIView.as_view(), name='health-check'),
]