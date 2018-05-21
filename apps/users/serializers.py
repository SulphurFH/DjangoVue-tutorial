import re
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator

from libs.normal_regex import REGEX_MOBILE
from config.redis_conf import MobileVerifyKind
from .backend import MobileVerifyCode

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :params data:
        :return:
        """
        # 手机是否注册
        if User.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError('用户已存在')

        # 手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError('请输入正确的手机号')

        return mobile


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = User
        fields = ("username", "gender", "birthday", "email", "mobile")


class UserRegSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])
    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )
    code = serializers.CharField(label='验证码', help_text='验证码', required=True, write_only=True, max_length=4,
                                 min_length=4, error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 })
    kind = serializers.ChoiceField(label='验证码类型', help_text='验证码类型', required=True, write_only=True,
                                   choices=list(MobileVerifyKind.values()))

    def validate_code(self, code):
        mobile = self.initial_data['mobile']
        status_code = MobileVerifyCode.verify_code(mobile, MobileVerifyKind['REGISTER'], code)
        if status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise serializers.ValidationError('验证码验证次数过多')
        elif status_code == status.HTTP_406_NOT_ACCEPTABLE:
            raise serializers.ValidationError('验证码错误')

    def validate(self, attrs):
        del attrs['code']
        del attrs['kind']
        return attrs

    class Meta:
        model = User
        fields = ('username', 'mobile', 'password', 'code', 'kind')