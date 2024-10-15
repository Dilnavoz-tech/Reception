from django.contrib import admin

from appointments.models import Appointment, WorkingHour

admin.site.register(Appointment)
admin.site.register(WorkingHour)