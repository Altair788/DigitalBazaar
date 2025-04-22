from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from network_nodes.filters import NetworkNodeFilter
from network_nodes.models import NetworkNode
from network_nodes.paginations import NetworkNodePaginator
from network_nodes.serializers import NetworkNodeSerializer
from users.permissions import IsActiveEmployee


class NetworkNodeCreateAPIView(generics.CreateAPIView):
    """
    Cоздание звеньев сети с фильтрацией по стране.
    """

    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (IsAuthenticated, IsActiveEmployee)


class NetworkNodeListAPIView(generics.ListAPIView):
    """
    Список звеньев сети с фильтрацией по стране.
    """

    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all().order_by("-created_at")
    pagination_class = NetworkNodePaginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = NetworkNodeFilter
    permission_classes = (IsAuthenticated, IsActiveEmployee)


class NetworkNodeRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение одного звена сети.
    """

    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (IsAuthenticated, IsActiveEmployee)


class NetworkNodeUpdateAPIView(generics.UpdateAPIView):
    """
    Обновление звена сети (запрещено менять задолженность через API).
    """

    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (IsAuthenticated, IsActiveEmployee)


class NetworkNodeDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление звена сети.
    """

    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (IsAuthenticated, IsActiveEmployee)
