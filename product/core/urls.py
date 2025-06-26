
from django.urls import path

from core.views import ProductAPIView, ProductAvgRatingAPIView, ProductCategoryCountAPIView, ProductIdAPIView, ProductPriceFilterAPIView, ProductVariantsAPIView, ProductsAPIView


urlpatterns = [
    path('products', ProductsAPIView.as_view(), name='api-products'),
    path('product/<str:slug>/', ProductAPIView.as_view(), name='api-product-detail'),
    path('product-id/<str:id>/', ProductIdAPIView.as_view(), name='api-product-detail-id'),
    path('product/rating/<str:id>', ProductAvgRatingAPIView.as_view()),
    path('variants', ProductVariantsAPIView.as_view()),
    path("products/filter-by-price", ProductPriceFilterAPIView.as_view(), name="filter-by-price"),   
    path('product-category-counts', ProductCategoryCountAPIView.as_view(), name='api-product-category-counts'),
]