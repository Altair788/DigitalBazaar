from django.urls import path

from network_nodes.apps import NetworkNodesConfig
from network_nodes.views import (
    NetworkNodeCreateAPIView,
    NetworkNodeDestroyAPIView,
    NetworkNodeListAPIView,
    NetworkNodeRetrieveAPIView,
    NetworkNodeUpdateAPIView,
)

app_name = NetworkNodesConfig.name

urlpatterns = [
    path("", NetworkNodeListAPIView.as_view(), name="network-nodes-list"),
    path("create/", NetworkNodeCreateAPIView.as_view(), name="network-nodes-create"),
    path(
        "<int:pk>/", NetworkNodeRetrieveAPIView.as_view(), name="network-nodes-retrieve"
    ),
    path(
        "update/<int:pk>/",
        NetworkNodeUpdateAPIView.as_view(),
        name="network-nodes-update",
    ),
    path(
        "delete/<int:pk>/",
        NetworkNodeDestroyAPIView.as_view(),
        name="network-nodes-delete",
    ),
]
