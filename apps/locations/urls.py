from rest_framework.routers import DefaultRouter

from .views import CountryViewSet, CityViewSet, AirportViewSet

router = DefaultRouter()
router.register('countries', CountryViewSet, basename='countries')
router.register('city', CityViewSet, basename='city')
router.register('airports', AirportViewSet, basename='airports')

urlpatterns = router.urls