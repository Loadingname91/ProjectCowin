from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken , AccessToken
from rest_framework_simplejwt.utils import aware_utcnow
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from UserSupportService.models import User
from UserSupportService.serializers.TokenObtainSerializers import MyTokenObtainPairSerializer, MyTokenRefreshSerializer
from UserSupportService.serializers.currentUserSerializer import CurrentUserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LogoutView(generics.DestroyAPIView):
    """
    Logout the user
    """

    def post(self, request):
        refresh_token = request.data['refresh']
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            outstanding_tokens = OutstandingToken.objects.filter(expires_at__lte=aware_utcnow())
            BlacklistedToken.objects.filter(token_id__in=outstanding_tokens).delete()
            outstanding_tokens.delete()
        except TokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)


class LogoutAllView(generics.DestroyAPIView):
    """
    Logout the user
    """

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)
        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)


class CurrentUserView(generics.CreateAPIView):
    serializer_class = CurrentUserSerializer
    queryset = User.objects.all()
    permission_classes = ()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        data.pop('password')
        return Response(data, status=status.HTTP_201_CREATED)

class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except TokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
