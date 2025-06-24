from django.urls import path

from core.views import CategoriesAPIView

urlpatterns = [
    path('categories', CategoriesAPIView.as_view(), name='api-categories'),
    # path('categories/product-related/<str:id>', CategoriesWithProductsAPIView.as_view(), name='api-productrelated'),
]