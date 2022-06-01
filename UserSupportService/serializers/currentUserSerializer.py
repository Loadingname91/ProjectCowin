from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from UserSupportService.models import User
from datetime import datetime, timezone


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'registeration_date', 'lastlogin_date', 'live_mode', 'is_default'
                  ,'state','city','zipcode','address','phone_number')
        ordering = ('email', 'registeration_date', 'lastlogin_date', 'live_mode', 'is_default')

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.registeration_date = validated_data["registeration_date"]
        instance.lastlogin_date = validated_data["lastlogin_date"]
        instance.live_mode = validated_data["live_mode"]
        instance.is_default = validated_data["is_default"]
        instance.state = validated_data["state"]
        instance.city = validated_data["city"]
        instance.zipcode = validated_data["zipcode"]
        instance.address = validated_data["address"]
        instance.phone_number = validated_data["phone_number"]
        instance.save()
        return instance

    def update_lastlogin(self, instance):
        instance.lastlogin_date = datetime.now(tz=timezone.utc)
        instance.save()
        return instance

    def validate_password(self, value):
        return make_password(value)
