import xadmin
from .models import Books, BooksCategory


class BooksAdmin(object):
    list_display = ['name', 'created_time', 'last_update', 'price']
    search_fields = ['name', ]
    list_filter = ['name', 'price']


class BooksCategoryAdmin(object):
    list_display = ['name', 'created_time', 'last_update', 'category_type']
    search_fields = ['name', ]
    list_filter = ['name', 'category_type']


xadmin.site.register(BooksCategory, BooksCategoryAdmin)
xadmin.site.register(Books, BooksAdmin)
