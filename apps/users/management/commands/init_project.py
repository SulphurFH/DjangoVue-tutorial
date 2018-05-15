import getpass
from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError
from django.db import transaction
from django.utils.termcolors import colorize
from django.contrib.auth.models import Group

from users.models import UserProfile


class Command(BaseCommand):

    def check_db(self):
        try:
            if len(UserProfile.objects.all()[:1]) > 0:
                pass
        except ProgrammingError:
            print(colorize("没有创建表", fg="red"))
            exit()

    def init_superuser(self):
        print(colorize("创建超级管理员", fg="cyan"))

        input_username = input(colorize("请输入用户名(必须是手机号,因为只有第一次部署才使用这个,不做校验了)", fg="yellow"))
        if input_username:
            username = input_username
        else:
            print(colorize("您没有输入,已结束流程.", fg="red"))
            exit()
        passwd1 = passwd2 = None
        while not (passwd1 and passwd2 and len(passwd1) >= 8 and passwd1 == passwd2):
            passwd1 = getpass.getpass(colorize("请输入密码(8位以上):", fg="yellow"))
            if not passwd1:
                continue
            passwd2 = getpass.getpass(colorize("请再次输入密码(8位以上):", fg="yellow"))

        with transaction.atomic():
            user = UserProfile.objects.create(
                id=1,
                username=username,
                is_staff=True,
                is_superuser=True
            )
            user.set_password(passwd2)
            user.save()
        self.user = user
        print(colorize("超级管理员账号创建成功", fg="green"))

    def init_group(self):
        group = Group.objects.create(
            id=1,
            name="超级群组",
        )
        self.group = group
        print(colorize("超级群组创建成功", fg="cyan"))

    def init_user_profile_group(self):
        self.user.groups.set([self.group])

    def handle(self, *args, **options):
        with transaction.atomic():
            self.check_db()
            self.init_superuser()
            self.init_group()
            self.init_user_profile_group()
