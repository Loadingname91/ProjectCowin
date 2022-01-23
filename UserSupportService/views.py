from rest_framework_simplejwt.views import TokenObtainPairView
from UserSupportService.serializers.TokenObtainSerializers import MyTokenObtainPairSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

