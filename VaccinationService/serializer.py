from rest_framework import serializers

from VaccinationService.models import VaccinationCenter, RegisterMember, Certificate


class RegisterMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterMember
        fields = '__all__'


class VaccinationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccinationCenter
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
