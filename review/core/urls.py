from django.urls import path

from core.views import ProductReviewSummaryAPIView, UserReviewAPIView

urlpatterns = [
    path('review', UserReviewAPIView.as_view(), name='api-create-review'),
    path('<str:id>', UserReviewAPIView.as_view(), name='api-list-review'),
    path('<str:product_id>/summary/', ProductReviewSummaryAPIView.as_view()),
]