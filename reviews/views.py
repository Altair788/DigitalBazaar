from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ads.models import Ad
from reviews.models import Review
from reviews.paginations import ReviewPaginator
from reviews.serializers import ReviewSerializer
from users.permissions import IsAdmin, IsAuthor


class ReviewCreateAPIView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (IsAdmin | IsAuthenticated,)

    def perform_create(self, serializer):
        ad_id = self.request.data.get("ad")
        ad = Ad.objects.get(id=ad_id)
        serializer.save(author=self.request.user, ad=ad)


class ReviewListAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all().order_by("-created_at")
    pagination_class = ReviewPaginator
    permission_classes = (IsAdmin | IsAuthenticated,)


class ReviewRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )


class ReviewUpdateAPIView(generics.UpdateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )


class ReviewDestroyAPIView(generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )
