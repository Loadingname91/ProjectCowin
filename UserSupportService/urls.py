from django.urls import path
from . import views

urlpatterns = [
    path('api/login/', views.MyTokenObtainPairView.as_view(), name='login'),
]