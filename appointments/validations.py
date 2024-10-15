from django.core.exceptions import ValidationError

from appointments.models import WorkingHour


def clean(self):
    if self.start_time >= self.end_time:
        raise ValidationError("Start time must be before end time.")

    overlapping_hours = WorkingHour.objects.filter(
        doctor=self.doctor,
        day_of_week=self.day_of_week,
        start_time__lt=self.end_time,
        end_time__gt=self.start_time,
    )
    if overlapping_hours.exists():
        raise ValidationError("This working hour overlaps with an existing schedule.")

    super().clean()
