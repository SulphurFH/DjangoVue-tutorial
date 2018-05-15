from django.http import Http404
from rest_framework import status, viewsets, mixins, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BooksSerializer, BooksCategorySerializer
from .models import Books, BooksCategory
from .filters import BooksFilter


class BooksListViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('name', 'category')
    filter_class = BooksFilter
    search_fields = ('name', 'desc')
    ordering_fields = ('id', 'price')


class BookDetailViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = BooksSerializer

    def get_object(self, pk):
        try:
            return Books.objects.get(pk=pk)
        except Books.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        book = self.get_object(pk)
        sr = BooksSerializer(book)
        return Response(sr.data)

    def put(self, request, pk, format=None):
        book = self.get_object(pk)
        sr = BooksSerializer(book, data=request.data)
        if sr.is_valid():
            sr.save()
            return Response(sr.data, status=status.HTTP_200_OK)
        return Response(sr.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        book = self.get_object(pk)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
