from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import get_object_or_404


# Create your models here.


class User(AbstractUser):
    twi_id = models.CharField(max_length=30, db_index=True, unique=True, null=True)
    twi_token = models.CharField(max_length=120, null=True)
    twi_token_secret = models.CharField(max_length=120, null=True)

    wei_id = models.CharField(max_length=30, db_index=True, unique=True, null=True)
    wei_token = models.CharField(max_length=60, null=True)
    wei_token_expire = models.DateTimeField(null=True)

    twi_head = models.BigIntegerField(null=True)
    twi_tail = models.BigIntegerField(null=True)

    wei_head = models.BigIntegerField(null=True)
    wei_tail = models.BigIntegerField(null=True)

    @property
    def is_linked_to_twi(self):
        return self.twi_id is not None

    @property
    def is_linked_to_wei(self):
        return self.wei_id is not None

    def update_fields(self, fields, instant_save=True):
        for field, value in fields.items():
            setattr(self, field, value)
        if instant_save:
            self.save()

    @staticmethod
    def merge_user(del_user, left_user, update_fields, by_join_order=False, instant_save=True):
        """ 合并两个 user， del_user 是合并后被删除的 user, left_user 是合并后保存的 user,
            update_fields 是手动更新的 fields， left_user 对应的 fields 会强制更新
            如果 by_join_order 为 True， 则不管传入的 user 顺序， 把加入时间靠后的用户删除
            这个函数的目的是为了简化以后可能会出现的比较复杂的用户合并情景
        """

        if by_join_order:
            del_user, left_user = sorted([del_user, left_user], key=lambda u: u.date_joined)

        for field in [x.name for x in left_user._meta.get_fields()]:
            # 不在手动更新序列中， 并且 left_user 这个 filed 的 value 为空， 则使用 del_user 的 value
            try:
                if field not in update_fields and not getattr(left_user, field):
                    if getattr(del_user, field):
                        setattr(left_user, field, getattr(del_user, field))
            except AttributeError:
                pass

        left_user.update_fields(update_fields, False)

        if instant_save:
            del_user.delete()
            left_user.save()

    @staticmethod
    def get(**kwargs):
        try:
            user = User.objects.get(**kwargs)
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_or_404(**kwargs):
        return get_object_or_404(User, **kwargs)


class UserBackend(ModelBackend):
    def authenticate(self, twi_id=None, wei_id=None, **kwargs):
        user = None
        try:
            if twi_id:
                user = User.objects.get(twi_id=twi_id)
            elif wei_id:
                user = User.objects.get(wei_id=wei_id)
        except User.DoesNotExist:
            pass
        return user
