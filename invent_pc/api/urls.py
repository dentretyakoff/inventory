from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CompCreateViewSet, HostCreateViewSet


# Версия API
API_VERSION = settings.API_VERSION

router = DefaultRouter()
router.register('comps', CompCreateViewSet)
router.register('vms', HostCreateViewSet)

urlpatterns = [
    path(f'{API_VERSION}/', include(router.urls)),
]
