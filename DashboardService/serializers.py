from rest_framework import serializers

from DashboardService.models import CovidNews


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CovidNews
        fields = '__all__'
