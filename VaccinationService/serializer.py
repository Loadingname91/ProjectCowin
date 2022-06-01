from rest_framework import serializers
from datetime import datetime
from VaccinationService.models import VaccinationCenter, RegisterMember, Certificate, SeatsAvailable


class RegisterMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterMember
        fields = ('user', 'status', 'set_alert', 'DateTimeRegistered')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context:
            data = {
                'user': instance.user.username,
                'status': instance.status,
                'set_alert': instance.set_alert,
                'DateTimeRegistered': instance.DateTimeRegistered,
                'first_dose_date': instance.first_dose_date,
                'second_dose_date': instance.second_dose_date
            }

        try:
            seats_available = SeatsAvailable.objects.get(registered_members=instance.id)
            data['center_registered'] = {
                'center_name': seats_available.center.name,
                'center_address': seats_available.center.address,
                'center_state': seats_available.center.state,
                'center_zip': seats_available.center.pin_code,
                'center_phone': seats_available.center.contact,
                'center_email': seats_available.center.email,
            }
        except SeatsAvailable.DoesNotExist:
            return data
        return data


class VaccinationCenterSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%d-%m-%Y", write_only=True)
    seats_available = serializers.IntegerField(write_only=True)

    class Meta:
        model = VaccinationCenter
        model_fields = (
            'id', 'name', 'address', 'contact', 'email', 'status', 'pin_code', 'district', 'state', 'country')
        extra_fields = ('date', 'seats_available')
        fields = model_fields + extra_fields

    def create(self, validated_data):
        seats_available = validated_data.pop('seats_available')
        date = validated_data.pop('date')
        center = VaccinationCenter.objects.create(**validated_data)
        SeatsAvailable.objects.create(center=center, seats_available=seats_available, date=date)
        return center


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'user': instance.user.username,
            'date_given': instance.date_given,
            'date_expiry': instance.date_expiry,
            'status': instance.status,
            'center': instance.center.name,
        }

    def create(self, validated_data):
        if 'register_member' in validated_data:
            registered_member = RegisterMember.objects.get(id=validated_data['register_member'])
            if validated_data["status"] == "first_dose":
                registered_member.first_dose_date = datetime.now()
            elif validated_data["status"] == "second_dose":
                registered_member.second_dose_date = datetime.now()
            registered_member.save()
        return Certificate.objects.create(**validated_data)


class SeatsAvailaVaccinationAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatsAvailable
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field in VaccinationCenterSerializer.Meta.model_fields:
            representation[field] = getattr(instance.center, field)
        representation.pop('registered_members')
        return representation
