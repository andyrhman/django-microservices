
from django.urls import path

from core.views import AdminReviewAPIView, TotalReviewsItemsAPIView

urlpatterns = [
    path('', AdminReviewAPIView.as_view()),
    path('<str:id>', AdminReviewAPIView.as_view()),
    path('total-reviews', TotalReviewsItemsAPIView.as_view())
]