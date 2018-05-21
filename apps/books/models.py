from django.db import models
from django.contrib.auth import get_user_model
from libs.models.mixins import TimeModelMixin

User = get_user_model()

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
    name = models.CharField(default="", max_length=30, verbose_name="类别名")
    category_type = models.SmallIntegerField(choices=CATEGORY_TYPE, verbose_name="类目级别")
    parent_category = models.ForeignKey('self', null=True, blank=True,
                                        verbose_name="父类目级别", on_delete=models.SET_NULL, related_name="sub_cat")

    class Meta:
        verbose_name = '类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Books(TimeModelMixin):
    """
    书籍models
    """
    name = models.CharField(max_length=30, verbose_name='书名')
    price = models.IntegerField(verbose_name='价值，单位分', default=0)
    desc = models.CharField(max_length=32, verbose_name='描述', default='')
    category = models.ForeignKey(BooksCategory, db_constraint=False, null=True,
                                 on_delete=models.SET_NULL, verbose_name="类别")
    creator = models.ForeignKey(User, db_constraint=False, on_delete=models.SET_NULL, null=True, verbose_name="创建者",
                                related_name='book_crt')
    last_editor = models.ForeignKey(User, db_constraint=False, on_delete=models.SET_NULL,
                                    null=True, verbose_name="最后修改者", related_name='book_edt')

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
