from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ads.filters import AdFilter
from ads.models import Ad
from ads.paginations import AdPaginator
from ads.serializers import AdSerializer
from users.permissions import IsAdmin, IsAuthor


class AdCreateAPIView(generics.CreateAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (IsAdmin | IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AdListAPIView(generics.ListAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all().order_by("-created_at")
    pagination_class = AdPaginator
    # подключение фильтрации
    filter_backends = [DjangoFilterBackend]
    # используемый фильтр
    filterset_class = AdFilter
    permission_classes = ()


class AdRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (IsAuthenticated | IsAdmin,)


class AdUpdateAPIView(generics.UpdateAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )


class AdDestroyAPIView(generics.DestroyAPIView):
    serializer_class = AdSerializer
    queryset = Ad.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdmin | IsAuthor,
    )
