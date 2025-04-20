from django.urls import path

from reviews.apps import ReviewsConfig
from reviews.views import (
    ReviewCreateAPIView,
    ReviewDestroyAPIView,
    ReviewListAPIView,
    ReviewRetrieveAPIView,
    ReviewUpdateAPIView,
)

app_name = ReviewsConfig.name

urlpatterns = [
    path("", ReviewListAPIView.as_view(), name="review-list"),
    path("create/", ReviewCreateAPIView.as_view(), name="review-create"),
    path("<int:pk>/", ReviewRetrieveAPIView.as_view(), name="review-retrieve"),
    path("update/<int:pk>/", ReviewUpdateAPIView.as_view(), name="review-update"),
    path(
        "delete/<int:pk>/",
        ReviewDestroyAPIView.as_view(),
        name="review-delete",
    ),
]
