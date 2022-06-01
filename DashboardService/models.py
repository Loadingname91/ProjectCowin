from django.db import models


# Create your models here.
class CovidNews(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField(max_length=200)
    dateadded = models.DateTimeField(auto_now_add=True)
    dateupdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Covid News"


class VaccinationRegionTrends(models.Model):
    id = models.AutoField(primary_key=True)
    region = models.CharField(max_length=200)
    trend = models.CharField(max_length=200)
    dateadded = models.DateTimeField(auto_now_add=True)
    dateupdated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.region

    class Meta:
        verbose_name_plural = "Vaccination Region Trends"

