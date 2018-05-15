from django.http import Http404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import BooksSerializer, BooksCategorySerializer
from .models import Books, BooksCategory


class BooksListView(generics.ListCreateAPIView):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer


class BookDetailView(APIView):
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


class BooksCategoryListView(generics.ListCreateAPIView):
    queryset = BooksCategory.objects.all()
    serializer_class = BooksCategorySerializer
