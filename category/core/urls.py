from django.urls import path

from core.views import CategoriesAPIView, CategoriesWithProductsAPIView, PublicCategoryListAPIView

urlpatterns = [
    path('categories', CategoriesAPIView.as_view(), name='api-categories'),
    path('categories/product-related/<str:id>', CategoriesWithProductsAPIView.as_view(), name='api-productrelated'),
    path('category', PublicCategoryListAPIView.as_view(), name='public-cats'),
    path('category/<uuid:id>', PublicCategoryListAPIView.as_view(), name='public-cat-detail'),
]