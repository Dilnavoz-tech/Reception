from django.urls import path
from django.urls import path
from .views import AppointmentViewSet, CheckAvailabilityViewSet, DoctorRecommendationViewSet

urlpatterns = [
    path('doctors/recommendations/', DoctorRecommendationViewSet.as_view({'get': 'doctor_list'})),
    path('appointments/', AppointmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='appointment-detail'),
    path('check-availability/', CheckAvailabilityViewSet.as_view({'get': 'check'}), name='check-availability'),
]
