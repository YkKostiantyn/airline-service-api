from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (AirplaneListCreateAPIView, AirlineListCreateAPIView,
                    AirplaneRetrieveUpdateDestroyAPIView,
                    AirlineRetrieveUpdateDestroyAPIView)

urlpatterns = [
    path('airlines/', AirlineListCreateAPIView.as_view(), name="airline_list_create"),
    path('airlines/<int:pk>/', AirlineRetrieveUpdateDestroyAPIView.as_view(), name='airline_detail'),
    path('airplanes/', AirplaneListCreateAPIView.as_view(), name="airplane_list_create"),
    path('airplanes/<int:pk>/', AirplaneRetrieveUpdateDestroyAPIView.as_view(), name='airplane_detail'),
]