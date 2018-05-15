from django.db import models
from libs.models.mixins import TimeModelMixin

# Create your models here.


class BooksCategory(TimeModelMixin):
    """
    类别models
    """
    CATEGORY_TYPE = (
        (1, "一级类别"),
        (2, "二级类别"),
        (3, "三级类别"),
    )
    name = models.CharField(default="", max_length=30, verbose_name="类别名", help_text="类别名")
    category_type = models.IntegerField(choices=CATEGORY_TYPE, verbose_name="类目级别", help_text="类目级别")

    class Meta:
        verbose_name = '类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Books(TimeModelMixin):
    """
    书籍models
    """
    name = models.CharField(max_length=30, verbose_name='书名', help_text='书名')
    category = models.ForeignKey(BooksCategory, db_constraint=False, null=True, on_delete=models.SET_NULL, verbose_name="类别")

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
