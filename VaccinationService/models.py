from datetime import date
from django.db import models
from UserSupportService.models import User
# Create your models here.

class RegisterMember(models.Model):
    id= models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    DateTimeRegistered = models.DateTimeField(default=date.today)
    status = models.CharField(max_length=150,null=False)