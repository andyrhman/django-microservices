from django.urls import path

from core.views import CategoriesAPIView, PublicCategoryListAPIView

urlpatterns = [
    path('', CategoriesAPIView.as_view(), name='api-categories'),
    path('category', PublicCategoryListAPIView.as_view(), name='public-cats'),
    path('category/<uuid:id>', PublicCategoryListAPIView.as_view(), name='public-cat-detail'),
]