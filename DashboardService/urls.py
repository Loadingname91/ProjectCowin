from django.urls import path
from . import views


urlpatterns = [
    path('add_covid_new/',views.CovidNewsDashboardView.as_view(),name='add_covid_news'),
    path('add_covid_new/<int:id>/',views.CovidNewsDashboardUpdate.as_view(),name='update_covid_news'),

]
