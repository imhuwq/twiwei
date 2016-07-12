from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.backends import ModelBackend


# Create your models here.


class User(AbstractUser):
    twi_id = models.CharField(max_length=30, db_index=True, unique=True, null=True)
    twi_token = models.CharField(max_length=120, null=True)
    twi_token_secret = models.CharField(max_length=120, null=True)

    wei_id = models.CharField(max_length=30, db_index=True, unique=True, null=True)
    wei_token = models.CharField(max_length=60, null=True)
    wei_token_expire = models.DateTimeField(null=True)

    def is_linked_to_twi(self):
        return self.twi_id is not None

    def is_linked_to_wei(self):
        return self.wei_id is not None


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
