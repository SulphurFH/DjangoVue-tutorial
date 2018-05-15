from rest_framework import serializers
from .models import Books, BooksCategory


class BooksCategorySerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = BooksCategory
        fields = '__all__'


class BooksSerializer(serializers.ModelSerializer):
    # TODO 没法外键显示
    # category = BooksCategorySerializer(read_only=True)
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Books
        fields = '__all__'
