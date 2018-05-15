from django_filters import rest_framework as filters
from .models import Books


class BooksFilter(filters.FilterSet):
    min_prize = filters.NumberFilter(name="price", lookup_expr='gte')
    max_prize = filters.NumberFilter(name="price", lookup_expr='lte')
    name = filters.CharFilter(name="name", lookup_expr='icontains')

    class Meta:
        model = Books
        fields = ('name', 'min_prize', 'max_prize', 'category')
