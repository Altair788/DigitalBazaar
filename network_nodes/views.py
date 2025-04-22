from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from network_nodes.models import NetworkNode
from network_nodes.paginations import NetworkNodePaginator
from network_nodes.serializers import NetworkNodeSerializer
from users.permissions import CanViewAPI
from network_nodes.filters import NetworkNodeFilter

class NetworkNodeListCreateAPIView(generics.ListCreateAPIView):
    """
    Список и создание звеньев сети с фильтрацией по стране.
    """
    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all().order_by("-created_at")
    pagination_class = NetworkNodePaginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = NetworkNodeFilter
    permission_classes = (CanViewAPI,)

class NetworkNodeRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение одного звена сети.
    """
    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (CanViewAPI,)

class NetworkNodeUpdateAPIView(generics.UpdateAPIView):
    """
    Обновление звена сети (запрещено менять задолженность через API).
    """
    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (CanViewAPI,)

class NetworkNodeDestroyAPIView(generics.DestroyAPIView):
    """
    Удаление звена сети.
    """
    serializer_class = NetworkNodeSerializer
    queryset = NetworkNode.objects.all()
    permission_classes = (CanViewAPI,)
