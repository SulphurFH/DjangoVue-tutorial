from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

from libs.models.mixins import TimeModelMixin

# Create your models here.


class UserProfile(AbstractUser):
    """
    用户
    """
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女")),
                              default="female", verbose_name="性别")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="手机号码")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class VerifyCode(TimeModelMixin):
    """
    短信验证码
    """
    code = models.CharField(max_length=4, verbose_name='验证码')
    mobile = models.CharField(max_length=11, verbose_name='手机号码')
    is_verified = models.BooleanField(default=False, verbose_name='是否验证')
    tried_times = models.IntegerField(default=0, null=False, verbose_name='尝试次数')
    kind = models.IntegerField(null=False, verbose_name='验证码类型')

    class Meta:
        verbose_name = '短信验证码'
        verbose_name_plural = verbose_name

    @classmethod
    def add_record(cls, mobile, code, kind):
        return cls.objects.create(mobile=mobile, code=code, kind=kind)

    @classmethod
    def update_record(cls, pk, tried_times, is_verified=True):
        return cls.objects.filter(id=pk).update(is_verified=is_verified, tried_times=tried_times,
                                                last_update=datetime.now())