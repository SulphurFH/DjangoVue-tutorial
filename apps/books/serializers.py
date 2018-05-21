from rest_framework import serializers
from .models import Books, BooksCategory


class FirstBooksCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksCategory
        fields = '__all__'


class SecondBooksCategorySerializer(serializers.ModelSerializer):
    sub_cat = FirstBooksCategorySerializer(many=True)

    class Meta:
        model = BooksCategory
        fields = '__all__'


class BooksCategorySerializer(serializers.ModelSerializer):
    sub_cat = SecondBooksCategorySerializer(many=True)
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = BooksCategory
        fields = '__all__'


class BooksSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    category_type = serializers.ReadOnlyField(source='category.category_type')
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_update = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    last_editor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Books
        fields = '__all__'
