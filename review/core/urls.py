from django.urls import path

from core.views import UserReviewAPIView

urlpatterns = [
    path('review', UserReviewAPIView.as_view(), name='api-create-review'),
    path('reviews/<str:id>', UserReviewAPIView.as_view(), name='api-list-review')
]