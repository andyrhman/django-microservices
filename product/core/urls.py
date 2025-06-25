
from django.urls import path

from core.views import ProductCategoryCountAPIView, ProductsAPIView


urlpatterns = [
    path('products', ProductsAPIView.as_view(), name='api-products'),
    # path('product/<str:slug>/', ProductAPIView.as_view(), name='api-product-detail'),
#     path('product/rating/<str:id>', ProductAvgRatingAPIView.as_view()),
#     path('variants', ProductVariantsAPIView.as_view()),
#     path('newly-added', NewlyAddedProductAPIView.as_view(), name='api-newlyadded'),
#     path('best-selling', BestSellingProductAPIView.as_view(), name='api-bestselling'),    
#     path("products/filter-by-price", ProductPriceFilterAPIView.as_view(), name="filter-by-price"),
    path('product-category-counts', ProductCategoryCountAPIView.as_view(), name='api-product-category-counts'),
]