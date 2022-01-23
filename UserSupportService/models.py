from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True)
    registeration_date = models.DateField(default=date.today)
    lastlogin_date = models.DateTimeField(null=True)
    live_mode = models.PositiveIntegerField(null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']