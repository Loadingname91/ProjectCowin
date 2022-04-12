import datetime
from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True)
    registeration_date = models.DateField(default=date.today)
    lastlogin_date = models.DateTimeField(default=datetime.datetime.now)
    live_mode = models.PositiveIntegerField(null=True)
    is_default = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']