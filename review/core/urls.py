from django.urls import path

from core.views import HealthCheckAPIView, ProductReviewSummaryAPIView, UserReviewAPIView

urlpatterns = [
    path('reviews/review', UserReviewAPIView.as_view(), name='api-create-review'),
    path('reviews/<str:id>', UserReviewAPIView.as_view(), name='api-list-review'),
    path('reviews/<str:product_id>/summary/', ProductReviewSummaryAPIView.as_view()),
    path('reviews/health/', HealthCheckAPIView.as_view(), name='api-health-check')
]