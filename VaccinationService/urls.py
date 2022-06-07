from django.urls import path
from . import views


urlpatterns = [
    path('members/', views.RegisterMemberViews.as_view(), name='register_member'),
    path('members_update_dose_info/', views.RegisterDoseInfo.as_view(), name='update_member_dose_info'),
    path('vaccination_center/', views.VaccinationServiceViews.as_view(), name='register_vaccine'),
    path('vaccination_center_all/',views.SeatsVaccinationCenterView.as_view(), name='seats_vaccine'),
    path('update_vaccination_center/<int:id>', views.VaccinationCenterViews.as_view(), name='update_vaccine'),
    path('certificate/', views.CertificateViews.as_view(), name='certificate'),
    path('add_self_vaccination_center/', views.AddSelfVaccinationCenterViews.as_view(), name='add_self_vaccine'),
    path('modify_alerts/',views.ModifyAlertsViews.as_view(), name='modify_alerts'),
    path('send_alerts/',views.SendAlertsViews.as_view(), name='send_alerts'),
    path('remove_vaccination_center/<int:id>', views.RemoveVaccinationCenterViews.as_view(), name='remove_vaccine'),
]