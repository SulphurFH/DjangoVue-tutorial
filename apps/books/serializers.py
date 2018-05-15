from rest_framework import serializers
from .models import Books, BooksCategory


class BooksCategorySerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = BooksCategory
        fields = '__all__'


class BooksSerializer(serializers.ModelSerializer):
    # category = BooksCategorySerializer(read_only=True)
    category_name = serializers.ReadOnlyField(source='category.name')
    category_type = serializers.ReadOnlyField(source='category.category_type')
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Books
        fields = '__all__'

    # TODO 自定义设置create
    # def create(self, validated_data):
    #     pass
