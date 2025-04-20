import django_filters

from ads.models import Ad


class AdFilter(django_filters.FilterSet):
    """
    Фильтр для поиска объявлений по названию.
    """

    # поиск будет регистронезависимым и будет искать частичное совпадение
    title = django_filters.CharFilter(lookup_expr="iregex", label="Название")

    class Meta:
        model = Ad
        fields = ["title"]
