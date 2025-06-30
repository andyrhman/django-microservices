from django.urls import path

from core.views import ProductReviewSummaryAPIView, UserReviewAPIView

urlpatterns = [
    path('review', UserReviewAPIView.as_view(), name='api-create-review'),
    path('reviews/<str:id>', UserReviewAPIView.as_view(), name='api-list-review'),
    path('reviews/<str:product_id>/summary/', ProductReviewSummaryAPIView.as_view()),
]