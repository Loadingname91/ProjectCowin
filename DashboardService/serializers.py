from rest_framework import serializers

from DashboardService.models import CovidNews, FAQ


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CovidNews
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'