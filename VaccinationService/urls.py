from django.urls import path
from . import views


urlpatterns = [
    path('members/', views.RegisterMemberViews.as_view(), name='register_member'),
    path('vaccination_center/', views.VaccinationServiceViews.as_view(), name='register_vaccine'),
    path('update_vaccination_center/<int:id>', views.VaccinationCenterViews.as_view(), name='update_vaccine'),
    path('certificate/', views.CertificateViews.as_view(), name='certificate'),
]