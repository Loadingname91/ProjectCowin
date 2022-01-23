from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from UserSupportService.serializers.currentUserSerializer import CurrentUserSerializer
from UserSupportService.models import User
from datetime import timedelta


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        user_details = CurrentUserSerializer(user).data
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user_details["email"]
        message = 'User with name ' + ' email ' + \
            user_details["email"] + ' logged in'
        return token

    def validate(self, attrs):
        serializer = CurrentUserSerializer()
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        serializer.update_lastlogin(User.objects.get(username=self.user))
        return data
