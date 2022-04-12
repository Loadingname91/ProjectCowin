from django.urls import path
from . import views
from .views import LogoutView, CurrentUserView, LogoutAllView

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logoutall/', LogoutAllView.as_view(), name='logoutall'),
    path('create_user/',CurrentUserView.as_view(), name='user-list'),
]