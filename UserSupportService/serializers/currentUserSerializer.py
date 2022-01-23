from rest_framework import serializers
from UserSupportService.models import User
from datetime import datetime, timezone

class CurrentUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'registeration_date', 'lastlogin_date', 'live_mode', 'is_default')
        ordering = ('email', 'registeration_date', 'lastlogin_date', 'live_mode', 'is_default')

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.registeration_date = validated_data["registeration_date"]
        instance.lastlogin_date = validated_data["lastlogin_date"]
        instance.live_mode = validated_data["live_mode"]
        instance.is_default = validated_data["is_default"]
        instance.save()
        return instance

    def update_lastlogin(self, instance):
        instance.lastlogin_date = datetime.now(tz=timezone.utc)
        instance.save()
        return instance
