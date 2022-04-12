from django.db.models import Q
from django.views.generic import ListView
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from VaccinationService.models import VaccinationCenter, RegisterMember, Certificate
from VaccinationService.serializer import VaccinationCenterSerializer, RegisterMembershipSerializer, \
    CertificateSerializer
from VaccinationService.validators import ValidateUserRole


class VaccinationServiceViews(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, ValidateUserRole]
    serializer_class = VaccinationCenterSerializer
    queryset = VaccinationCenter.objects.all()

    def filter_queryset(self, queryset):
        if self.request.method == 'GET':
            query = self.request.GET.get('name', "")
            if query:
                value = queryset.filter(Q(name__icontains=query) | Q(address__icontains=query)).all()
                return value
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        if len(result) == 0:
            return Response({'message': 'No data found'}, status=status.HTTP_200_OK)

        return Response(result)


class VaccinationCenterViews(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, ValidateUserRole]
    serializer_class = VaccinationCenterSerializer
    queryset = VaccinationCenter.objects.all()


class RegisterMemberViews(generics.ListCreateAPIView):
    lookup_field = 'id'
    queryset = RegisterMember.objects.all()
    serializer_class = RegisterMembershipSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user_id=request.user.id)
        if len(queryset) == 0:
            return Response({'message': 'No data found'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.user.id
        is_user_registered = self.get_queryset().filter(user_id=user_id).exists()
        if is_user_registered:
            return Response({'message': 'User already registered'}, status=status.HTTP_200_OK)
        serializer.save(user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().get(user_id=request.user.id)
            request_data = request.data
            serializer = self.get_serializer(queryset,data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RegisterMember.DoesNotExist:
            return Response({'message': 'User not registered'}, status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class CertificateViews(RegisterMemberViews):
    serializer_class = CertificateSerializer


    def get_queryset(self):
        register_member_id = self.request.GET.get('id', "")
        if register_member_id:
            return Certificate.objects.filter(id=id, user_id=self.request.user.id)

        return Certificate.objects.filter(user_id=self.request.user.id)

    def get_co_model_queryset(self,user_id):
        try:
            registered_member = RegisterMember.objects.get(user_id=user_id)
            return registered_member
        except RegisterMember.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.user.id
        is_user_registered = self.get_co_model_queryset(user_id)
        if is_user_registered and (
                is_user_registered.second_dose_date and is_user_registered.first_dose_date):
            serializer.save(user_id=request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': 'User not registered'}, status=status.HTTP_200_OK)
