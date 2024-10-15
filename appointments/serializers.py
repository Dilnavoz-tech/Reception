from datetime import timezone

from rest_framework import serializers

from appointments.models import Appointment
from authentication.models import User
from authentication.serializers import UserSerializer


class AlternativeTimeSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()

class AvailabilitySerializer(serializers.Serializer):
    available = serializers.BooleanField()
    doctor = serializers.IntegerField(required=False)
    datetime = serializers.DateTimeField(required=False)
    alternatives = serializers.DictField(
        child=serializers.ListField(
            child=serializers.IntegerField(),
            required=False
        ),
        required=False
    )
    alternative_times = AlternativeTimeSerializer(many=True, required=False)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Only include 'alternatives' when 'available' is False
        if not representation.get('available'):
            representation['alternatives'] = {
                'doctors': instance.get('alternative_doctors', []),
                'times': instance.get('alternative_times', [])
            }
        return representation


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(read_only=True)
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=2),
        source='doctor',
        write_only=True
    )
    patient = UserSerializer(read_only=True)
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=3),
        source='patient',
        write_only=True
    )

    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'doctor_id', 'patient', 'patient_id', 'date_time', 'status']
        read_only_fields = ['id']

    def validate_date_time(self, value):
        """Ensure the date_time is in the future."""
        if value < timezone.now():
            raise serializers.ValidationError("Appointment time must be in the future.")
        return value

    def create(self, validated_data):
        """Create a new appointment instance."""
        return Appointment.objects.create(**validated_data)

