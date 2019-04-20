from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser

from .managers import UserManager


class DownloadedFile(models.Model):
    created_date = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    year = models.IntegerField()
    percent = models.DecimalField(max_digits=7, decimal_places=2)
    project_name = models.CharField(max_length=255)
    irr = models.CharField(max_length=255)


class IncomeOutgo(models.Model):
    file = models.ForeignKey(DownloadedFile, on_delete=models.CASCADE)
    row = models.IntegerField()
    income = models.DecimalField(max_digits=16, decimal_places=2)
    outgo = models.DecimalField(max_digits=16, decimal_places=2)


class User(AbstractBaseUser):
    ADMIN, INVESTOR = range(1, 3)
    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (INVESTOR, 'investor'),
    )

    role = models.IntegerField('Role', choices=ROLE_CHOICES, default=ADMIN)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField('email address', max_length=255, unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def full_name(self):
        return self.first_name + ' ' + self.last_name
