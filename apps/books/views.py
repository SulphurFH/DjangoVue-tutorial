from rest_framework import viewsets, mixins, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import BooksSerializer, BooksCategorySerializer
from .models import Books, BooksCategory
from .filters import BooksFilter
from libs.permissions import IsOwnerOrReadOnly


class BooksListViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    list:
        Books list
    create:
        Create Book
    retrieve:
        return a Book instance
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = BooksSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('name', 'category')
    filter_class = BooksFilter
    search_fields = ('name', 'desc')
    ordering_fields = ('id', 'price', 'created_time')
    ordering = ('-created_time',)
    # 自定义搜索字段
    # lookup_fields

    def get_queryset(self):
        return Books.objects.filter(creator=self.request.user)


class BooksCategoryListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        书籍类别列表
    """
    serializer_class = BooksCategorySerializer
    ordering = ('category_type')

    def get_queryset(self):
        id_min = self.request.query_params.get('id_min', 0)
        queryset = BooksCategory.objects.all()
        if id_min:
            queryset = queryset.filter(pk__gt=int(id_min))
        return queryset
