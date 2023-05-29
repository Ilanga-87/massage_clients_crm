# products/filters.py
from decimal import Decimal
from django.db.models import Q
import django_filters
from .models import Client


class ClientFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='universal_search',
                                      label="")

    class Meta:
        model = Client
        fields = ['query']

    def universal_search(self, queryset, name, value):
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return Client.objects.filter(
                Q(price=value) | Q(cost=value)
            )
        # TODO: which fields can need digit check? If none, it is better to delete this check.
        #  Anyway fields must be changed
        return Client.objects.filter(
            Q(name__icontains=value) | Q(category__icontains=value)
        )
