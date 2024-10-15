from django.db import models  # Ensure this import is at the top of your file
from authentication.models import User  # Assuming User model is in authentication app

class Appointment(models.Model):  # Use models.Model instead of Model here
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 2}  # Role '2' corresponds to Doctor
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 3}  # Role '3' corresponds to Patient
    )
    date_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[('scheduled', 'Scheduled'), ('canceled', 'Canceled')]
    )

    def __str__(self):
        return f"{self.doctor.username} with {self.patient.username} on {self.date_time}"

class WorkingHour(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='working_hours',
        limit_choices_to={'role': 2}  #2 Doctor
    )
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.username}'s hours on {self.get_day_of_week_display()}: {self.start_time} - {self.end_time}"

