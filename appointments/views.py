from rest_framework.permissions import IsAuthenticated

from authentication.serializers import UserSerializer
from .serializers import AppointmentSerializer
from notifications.utils import send_telegram_notification
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Appointment, User, WorkingHour
from .serializers import AvailabilitySerializer


class DoctorRecommendationViewSet(viewsets.ViewSet):
    def doctor_list(self, request):
        doctors = User.objects.filter(role=2)  #2 Doctor
        serializer = UserSerializer(doctors, many=True)
        return Response(serializer.data)


class CheckAvailabilityViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('username', openapi.IN_QUERY, description="Username of the doctor", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('date', openapi.IN_QUERY, description="Appointment date (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('time', openapi.IN_QUERY, description="Appointment time (HH:MM)", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Response(
                description="Availability Check",
                schema=AvailabilitySerializer
            ),
            400: 'Bad Request - Invalid Parameters',
            404: 'Not Found - Doctor not found',
        },
        operation_summary="Check Doctor Availability by Username",
        operation_description="Checks if the specified doctor is available at the given date and time using the doctor's username. Returns alternative doctors or times if unavailable."
    )
    @action(detail=False, methods=['get'])
    def check(self, request):
        username = request.query_params.get('username')
        date = request.query_params.get('date')
        time = request.query_params.get('time')
        appointment_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')

        try:
            doctor = User.objects.get(username=username, role=2)
        except User.DoesNotExist:
            return Response({"detail": "Doctor not found."}, status=404)

        doctor_appointments = Appointment.objects.filter(
            doctor=doctor,
            date_time=appointment_datetime,
            status='scheduled'
        )

        if not doctor_appointments.exists():
            return Response({"available": True, "doctor": doctor.username, "datetime": appointment_datetime})

        alternative_doctors = User.objects.filter(
            role=2,
            working_hours__day_of_week=appointment_datetime.weekday(),
            working_hours__start_time__lte=appointment_datetime.time(),
            working_hours__end_time__gte=(appointment_datetime + timedelta(hours=1)).time()
        ).exclude(id=doctor.id)

        alternative_times = WorkingHour.objects.filter(
            doctor=doctor,
            day_of_week=appointment_datetime.weekday()
        ).exclude(
            start_time__gte=appointment_datetime.time(),
            end_time__lte=(appointment_datetime + timedelta(hours=1)).time()
        )

        response_data = {
            "available": False,
            "alternatives": {
                "doctors": [doc.username for doc in alternative_doctors],
                "times": [
                    {"start_time": str(t.start_time), "end_time": str(t.end_time)}
                    for t in alternative_times
                ]
            }
        }
        return Response(response_data)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'doctor_username', openapi.IN_QUERY, description="Username of the doctor",
                type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                'patient_username', openapi.IN_QUERY, description="Username of the patient",
                type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                'date', openapi.IN_QUERY, description="Appointment date in YYYY-MM-DD format",
                type=openapi.TYPE_STRING, required=True
            ),
            openapi.Parameter(
                'time', openapi.IN_QUERY, description="Appointment time in HH:MM format",
                type=openapi.TYPE_STRING, required=True
            )
        ],
        responses={
            201: openapi.Response(
                description="Appointment created successfully",
                schema=AppointmentSerializer
            ),
            400: "Bad Request - Invalid date or time format",
            404: "Not Found - Doctor or patient not found",
        },
        operation_summary="Create an Appointment",
        operation_description="Creates a new appointment by providing the doctor and patient usernames, as well as the appointment date and time as query parameters."
    )
    def create(self, request, *args, **kwargs):
        doctor_username = request.query_params.get('doctor_username')
        patient_username = request.query_params.get('patient_username')
        date = request.query_params.get('date')
        time = request.query_params.get('time')

        try:
            doctor = User.objects.get(username=doctor_username, role=2)
            patient = User.objects.get(username=patient_username, role=3)

            from django.utils import timezone

            appointment_datetime = timezone.make_aware(datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M'))

            if Appointment.objects.filter(doctor=doctor, patient=patient, date_time=appointment_datetime).exists():
                return Response({'error': 'An appointment already exists for this time.'},
                                status=status.HTTP_400_BAD_REQUEST)

            appointment = Appointment.objects.create(
                doctor=doctor,
                patient=patient,
                date_time=appointment_datetime,
                status='scheduled'
            )

            serializer = AppointmentSerializer(appointment)
            headers = self.get_success_headers(serializer.data)

            send_telegram_notification(appointment, "scheduled")
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except User.DoesNotExist:
            return Response({'error': 'Doctor or patient not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Invalid date or time format.'}, status=status.HTTP_400_BAD_REQUEST)



