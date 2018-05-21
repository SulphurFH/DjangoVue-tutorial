from django_filters import rest_framework as filters
from .models import Books


class BooksFilter(filters.FilterSet):
    # help_text为API文档字段说明
    min_prize = filters.NumberFilter(name="price", lookup_expr='gte', help_text='')
    max_prize = filters.NumberFilter(name="price", lookup_expr='lte')
    name = filters.CharFilter(name="name", lookup_expr='icontains')

    class Meta:
        model = Books
        fields = ('name', 'min_prize', 'max_prize', 'category')
