from datetime import datetime
from django.db import models
from UserSupportService.models import User


# Create your models here.

class RegisterMember(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    DateTimeRegistered = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=150, null=False)
    first_dose_date = models.DateField(null=True)
    second_dose_date = models.DateField(null=True)
    set_alert = models.BooleanField(default=False)


class VaccinationCenter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, null=False)
    address = models.CharField(max_length=150, null=False)
    contact = models.CharField(max_length=150, null=False)
    email = models.CharField(max_length=150, null=False)
    status = models.CharField(max_length=150, null=False)
    pin_code = models.IntegerField(null=False)
    district = models.CharField(max_length=150, null=False)
    state = models.CharField(max_length=150, null=False)
    country = models.CharField(max_length=150, null=False)


class SeatsAvailable(models.Model):
    id = models.AutoField(primary_key=True)
    center = models.ForeignKey(VaccinationCenter, on_delete=models.CASCADE)
    date = models.DateField(null=False)
    registered_members = models.ManyToManyField(RegisterMember, blank=True, related_name='registered_members')
    seats_available = models.IntegerField()
    date_time_updated = models.DateTimeField(auto_now=True)


class Certificate(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_given = models.DateField(null=False)
    date_expiry = models.DateField(null=False)
    status = models.CharField(max_length=150, null=False)
    center = models.ForeignKey(VaccinationCenter,on_delete=models.CASCADE)
    registered_member = models.ForeignKey(RegisterMember, on_delete=models.CASCADE)
