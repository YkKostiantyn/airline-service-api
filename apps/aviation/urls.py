from rest_framework.routers import DefaultRouter
from .views import AirlineViewSet, AirplaneViewSet

router = DefaultRouter()
router.register('airlines', AirlineViewSet, basename='airlines')
router.register('airplanes', AirplaneViewSet, basename='airplanes')

urlpatterns = router.urls