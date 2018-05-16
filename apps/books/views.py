from django.http import Http404
from rest_framework import status, viewsets, mixins, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BooksSerializer, BooksCategorySerializer
from .models import Books, BooksCategory
from .filters import BooksFilter


class BooksListViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    List:
        书籍列表
    """
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('name', 'category')
    filter_class = BooksFilter
    search_fields = ('name', 'desc')
    ordering_fields = ('id', 'price', 'created_time')
    ordering = ('-created_time',)


class BooksCategoryListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    # queryset = BooksCategory.objects.all()
    serializer_class = BooksCategorySerializer

    def get_queryset(self):
        id_min = self.request.query_params.get('id_min', 0)
        queryset = BooksCategory.objects.all()
        if id_min:
            queryset = queryset.filter(pk__gt=int(id_min))
        return queryset
        # return Response(queryset.data)
