import random
from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from config.redis_conf import MobileVerifyKind
from libs.permissions import IsOwnerOrReadOnly
from .serializers import UserRegSerializer, UserDetailSerializer, SmsSerializer
from .backend import MobileVerifyCode

User = get_user_model()


class SmsCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for _ in range(4):
            random_str.append(random.choice(seeds))

        return ''.join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        # 此处要真对code做判断是否发送成功
        is_success, code = MobileVerifyCode.require_send_code(mobile, MobileVerifyKind['REGISTER'])
        if is_success:
            return Response({'code': code, 'mobile': mobile}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=code)


class UserViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated(), ]
        elif self.action == 'create':
            return []
        return []

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer

        return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["name"] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        # mixins.RetrieveModelMixin/mixins.DeleteModelMixin 都会用到
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()
