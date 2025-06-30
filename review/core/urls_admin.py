
from django.urls import path

from core.views import AdminReviewAPIView, TotalReviewsItemsAPIView

urlpatterns = [
    path('reviews', AdminReviewAPIView.as_view()),
    path('reviews/<str:id>', AdminReviewAPIView.as_view()),
    path('total-reviews', TotalReviewsItemsAPIView.as_view())
]