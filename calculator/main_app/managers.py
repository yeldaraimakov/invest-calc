from django.db import models

from django.contrib.auth.models import BaseUserManager


class UserQuerySet(models.QuerySet):
    def get_queryset(self):
        return self.get_queryset()


class UserManager(BaseUserManager):
    def get_all(self):
        return UserQuerySet(self.model, using=self._db)

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).all()

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.save(using=self.db)
        return user

    def create_investor(self, email, password, first_name, last_name):
        user = self.create_user(email, password)
        user.is_staff = True
        user.role = 2  # investor role
        user.first_name = first_name
        user.last_name = last_name
        user.save(using=self.db)
        return user
