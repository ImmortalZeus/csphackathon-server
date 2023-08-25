from django.db import models
from django.contrib.auth.models import User
import json, os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError

# Create your models here.

class ContestantManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Người dùng phải có username')
        
        user = self.model(
            username = username,
        )

        user.set_password(password)

        user.save(using=self._db)

        return user


    def create_superuser(self, username, password):        
        user = self.create_user(
            username = username,
            password = password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        
        user.save(using=self._db)

        return user

class Contestant(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    # ba cái is_active, is_admin, is_staff, is_superuser ĐỪNG CÓ XÓA
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    members = models.JSONField(default=dict, null=True, blank=True)
    firstac = models.JSONField(default=dict, null=True, blank=True)
    score = models.JSONField(default=dict, null=True, blank=True)
    penalty = models.JSONField(default=dict, null=True, blank=True)
    submissions = models.JSONField(default=dict, null=True, blank=True)
    submitted = models.BooleanField(default=False)
    tscore = models.IntegerField(default=0)
    tpenalty = models.IntegerField(default=0)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True) # ko cần quan tâm cái này lắm
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True, auto_now=False) # ko cần quan tâm cái này lắm
    
    objects = ContestantManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class Problem(models.Model):
    name = models.CharField(max_length=255, unique=True)
    testnum = models.IntegerField(default=1) # số testcase
    mscore = models.IntegerField(default=100) # max score (điểm tối đa từng bài)
    submissions = models.JSONField(default=list, null=True, blank=True)
    ordered = models.BooleanField(default=True)
    unsolved = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LeaderBoard(models.Model):
    name = models.CharField(max_length=255, unique=True, default="rankingsave")
    value = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name