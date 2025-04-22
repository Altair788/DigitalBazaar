import django_filters

from network_nodes.models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        lookup_expr="icontains", label="Страна (поиск по части названия)"
    )

    class Meta:
        model = NetworkNode
        fields = ["country"]
