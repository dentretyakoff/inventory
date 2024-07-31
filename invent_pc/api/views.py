from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from comps.models import Comp, Host
from .serializers import CompSerializer, HostCreateSerializer


class CompCreateViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    queryset = Comp.objects.all()
    serializer_class = CompSerializer

    def get_object(self):
        comp = get_object_or_404(Comp, pc_name=self.request.data['pc_name'])
        return comp

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class HostCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    queryset = Host.objects.all()
    serializer_class = HostCreateSerializer
