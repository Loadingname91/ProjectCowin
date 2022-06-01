from django.shortcuts import render

# Create your views here.
from rest_framework import generics, filters, status
from rest_framework.response import Response

from DashboardService.models import CovidNews
from DashboardService.serializers import NewsSerializer
from VaccinationService.validators import ValidateUserRole


class CovidNewsDashboardView(generics.ListCreateAPIView):
    """
    View for the Covid News Dashboard
    """
    serializer_class = NewsSerializer
    queryset = CovidNews.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        """
        This view should return a list of all the news
        for the covid19 news dashboard
        """
        return CovidNews.objects.all()

    def create(self, request, *args, **kwargs):
        """
        This view should create a new news item
        """
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request):
            return Response(data={'message': 'You do not have permission to create a news item'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CovidNewsDashboardUpdate(generics.UpdateAPIView):
    """
    View for updating a news item
    """
    serializer_class = NewsSerializer
    queryset = CovidNews.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        """
        This view should update a news item
        """
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request):
            return Response(data={'message': 'You do not have permission to update a news item'},
                            status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
