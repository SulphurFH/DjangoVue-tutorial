import re
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from libs.normal_regex import REGEX_MOBILE
from .models import VerifyCode

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    model = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :params data:
        :return:
        """
        # 手机是否注册
        if User.objects.filter(mobile=mobile).exits():
            raise serializers.ValidationError('用户已存在')

        # 手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError('请输入正确的手机号')

        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, mintes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gte=one_mintes_ago, mobile=mobile).exits():
            raise serializers.ValidationError('验证码发送太频繁')

        return mobile


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = User
        fields = ("name", "gender", "birthday", "email", "mobile")


class UserRegSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    class Meta:
        model = User
        fields = ("username", "password")