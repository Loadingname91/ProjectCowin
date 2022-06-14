from datetime import datetime, timedelta

import pytz
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ProjectCovid import settings
from VaccinationService.models import VaccinationCenter, RegisterMember, Certificate, SeatsAvailable
from VaccinationService.serializer import VaccinationCenterSerializer, RegisterMembershipSerializer, \
    CertificateSerializer, SeatsAvailaVaccinationAppointmentSerializer
from VaccinationService.validators import ValidateUserRole


class VaccinationServiceViews(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VaccinationCenterSerializer
    queryset = VaccinationCenter.objects.all()

    def filter_queryset(self, queryset):
        if self.request.method == 'GET':
            if self.request.GET.get('name', ""):
                query = self.request.GET.get('name', "")
            elif self.request.GET.get('pin_code', ""):
                query = self.request.GET.get('pin_code', "")
            if query:
                value = queryset.filter(Q(name__icontains=query) | Q(address__icontains=query) |
                                        Q(pin_code__icontains=query)).all()
                return value
        return queryset

    def create(self, request, *args, **kwargs):
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        validate_user = ValidateUserRole()
        if not validate_user.has_permission(request) and not request.GET.get('name', "") \
                and not request.GET.get('pin_code', ""):
            return Response(data={"message": "You do not have premission to perform this action"},
                            status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        vaccination_details = serializer.data
        if validate_user.has_permission(request):
            for center in vaccination_details:
                seats_available = SeatsAvailable.objects.filter(center=center['id']).all()
                for seat in seats_available:
                    center['seats_info'] = {
                        "seats_available": seat.seats_available,
                        "date": seat.date,
                        "register_member": RegisterMembershipSerializer(seat.registered_members, many=True).data
                    }
        return Response(vaccination_details)


class SeatsVaccinationCenterView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SeatsAvailaVaccinationAppointmentSerializer
    queryset = SeatsAvailable.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        if len(result) == 0:
            return Response({'message': 'No data found'}, status=status.HTTP_200_OK)
        return Response(result)

    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super(SeatsVaccinationCenterView, self).handle_exception(exc)


class VaccinationCenterViews(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, ValidateUserRole]
    serializer_class = VaccinationCenterSerializer
    queryset = VaccinationCenter.objects.all()
    lookup_field = 'id'

    def patch(self, request, *args, **kwargs):
        data = request.data['registered_members']
        success = []
        failure = []
        print(data)
        for member in data:
            try:
                member_obj = RegisterMember.objects.get(user__username=member)
                seats_available = SeatsAvailable.objects.get(center__id=kwargs['id'])
                print(seats_available)
                if seats_available.seats_available > 0:
                    seats_available.seats_available -= 1
                    try:
                        if seats_available.registered_members.get(user__username=member):
                            failure.append(member)
                    except RegisterMember.DoesNotExist:
                        seats_available.registered_members.add(member_obj)
                        success.append(member)
                        seats_available.save()
                    else:
                        seats_available.registered_members.add(member_obj)
                        seats_available.save()
                        seats_available.save()
                        success.append(member_obj.user.username)
            except RegisterMember.DoesNotExist:
                failure.append(member)
            except serializers.ValidationError:
                failure.append(member)

        success_response = {
            'success': success,
        }
        failure_response = {
            'failure': failure,
        }
        if len(success) > 0:
            success_response['message'] = 'Successfully registered'
        elif len(failure) > 0:
            failure_response['message'] = 'Failed to register'
        return Response({"success": success_response, "failure": failure_response})

    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        else:
            print(exc)
            return super(VaccinationCenterViews, self).handle_exception(exc)


class RegisterMemberViews(generics.ListCreateAPIView):
    lookup_field = 'id'
    queryset = RegisterMember.objects.all()
    serializer_class = RegisterMembershipSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        validate_user = ValidateUserRole()
        is_admin = validate_user.has_permission(request)
        queryset = self.get_queryset()
        if not is_admin:
            queryset = self.get_queryset().filter(user_id=request.user.id)
        if len(queryset) == 0:
            return Response({'message': 'No data found'}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True, context=is_admin)
        member_data = serializer.data
        print(member_data)
        return Response(member_data)

    def post(self, request, *args, **kwargs):
        print(request.user.id)
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.user.id
        is_user_registered = self.get_queryset().filter(user_id=user_id).exists()
        if is_user_registered:
            return Response({'message': 'User already registered'}, status=status.HTTP_200_OK)
        serializer.save(user_id=request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterDoseInfo(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, ValidateUserRole]
    queryset = RegisterMember.objects.all()
    serializer_class = RegisterMembershipSerializer

    def patch(self, request, *args, **kwargs):
        instance = RegisterMember.objects.filter(user__username=request.data['user_name']).first()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CertificateViews(generics.ListCreateAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        register_member_id = self.request.GET.get('id', "")
        if register_member_id:
            return Certificate.objects.filter(id=id, user_id=self.request.user.id)

        return Certificate.objects.filter(user_id=self.request.user.id)

    def get_co_model_queryset(self, user_id):
        try:
            registered_member = RegisterMember.objects.get(user_id=user_id)
            return registered_member
        except RegisterMember.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        if len(serializer.data) == 0:
            return Response({'message': 'No data found'}, status=status.HTTP_200_OK)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.data['user']
        is_user_registered = self.get_co_model_queryset(user_id)
        if is_user_registered and (
                not is_user_registered.second_dose_date or not is_user_registered.first_dose_date):
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': 'User already has a completed certificate'}, status=status.HTTP_200_OK)


class AddSelfVaccinationCenterViews(generics.ListCreateAPIView):
    queryset = SeatsAvailable.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            register_member = RegisterMember.objects.get(user_id=request.user.id)
        except RegisterMember.DoesNotExist:
            return Response({'message': 'User not registered'}, status=status.HTTP_200_OK)
        present_instance = SeatsAvailable.objects.filter(registered_members__user_id=request.user.id)
        if present_instance.exists():
            data['center_name'] = present_instance.first().center.name
            data['message'] = 'User already has registered to a vaccination center'
            return Response(data, status=status.HTTP_200_OK)
        seats_available_instance = SeatsAvailable.objects.get(center=data['center'])
        if seats_available_instance.seats_available > 0:
            if seats_available_instance.registered_members.filter(id=register_member.id).exists():
                return Response({'message': 'User already registered'}, status=status.HTTP_200_OK)
            else:
                seats_available_instance.seats_available = seats_available_instance.seats_available - 1
                seats_available_instance.registered_members.add(register_member)
                seats_available_instance.save()
                return Response({'message': 'User registered successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No seats available'}, status=status.HTTP_200_OK)


class ModifyAlertsViews(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = RegisterMember.objects.all()

    def patch(self, request, *args, **kwargs):
        data = request.data
        try:
            register_member = RegisterMember.objects.get(user_id=request.user.id)
        except RegisterMember.DoesNotExist:
            return Response({'message': 'User not registered'}, status=status.HTTP_200_OK)
        if data['alert_status'] == 'True':
            register_member.set_alert = True
        else:
            register_member.set_alert = False
        register_member.save()
        return Response({'message': 'Alert status updated successfully'}, status=status.HTTP_200_OK)


class SendAlertsViews(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ValidateUserRole]
    queryset = RegisterMember.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            recipent_members = []
            for seats_available in SeatsAvailable.objects.all():
                if abs(seats_available.date_time_updated - datetime.now(pytz.utc)).days >= 1:
                    for member in seats_available.registered_members.all():
                        if member.set_alert and seats_available.seats_available > 0:
                            recipent_members.append(member.user.email)
            if len(recipent_members) == 0:
                return Response({'message': 'No members to send alerts'}, status=status.HTTP_200_OK)
            send_mail(
                'Hello from Vaccination Center',
                'The vaccination center has some seats available which you can book',
                settings.EMAIL_HOST_USER,
                recipent_members,
            )
            return Response({'message': 'Alert sent successfully'}, status=status.HTTP_200_OK)
        except RegisterMember.DoesNotExist:
            return Response({'message': 'User not registered'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error in sending alert'}, status=status.HTTP_200_OK)


class RemoveVaccinationCenterViews(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, ValidateUserRole]
    queryset = SeatsAvailable.objects.all()
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        try:
            vaccination_center = self.get_queryset().get(center=kwargs['id'])
            vaccination_center.center.delete()
            vaccination_center.registered_members.clear()
            vaccination_center.delete()
            return Response({'message': 'Vaccination center deleted successfully'}, status=status.HTTP_200_OK)
        except VaccinationCenter.DoesNotExist:
            return Response({'message': 'Vaccination center not found'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error in deleting vaccination center'}, status=status.HTTP_200_OK)
