from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _




class User(AbstractUser):
    username = models.CharField(default=False,blank=False, max_length=100, unique=True)
    email = models.EmailField(default=False, blank=False)
    phone = models.CharField(max_length=12)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'phone']
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Cart(models.Model):
    customer_name = models.CharField('Customer name', max_length=200)
