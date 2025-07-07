from django.urls import path

from core.views import CategoriesAPIView, HealthCheckAPIView, PublicCategoryListAPIView

urlpatterns = [
    path('categories', CategoriesAPIView.as_view(), name='api-categories'),
    path('categories/category', PublicCategoryListAPIView.as_view(), name='public-cats'),
    path('categories/category/<uuid:id>', PublicCategoryListAPIView.as_view(), name='public-cat-detail'),
    path('categories/health', HealthCheckAPIView.as_view(), name='health-check'),
]