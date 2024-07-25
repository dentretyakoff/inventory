# comps/filters.py
from datetime import timedelta

import django_filters
from django.utils import timezone

from .models import Comp, ItemsChoices, Disk, Ram, Monitor


class CompFilter(django_filters.FilterSet):
    pc_name = django_filters.CharFilter(
        field_name='pc_name',
        lookup_expr='icontains'
    )
    days = django_filters.NumberFilter(method='filter_by_online_date')
    disks = django_filters.BooleanFilter(method='filter_lost_disks')
    rams = django_filters.BooleanFilter(method='filter_lost_rams')
    monitors = django_filters.BooleanFilter(method='filter_lost_monitors')

    class Meta:
        model = Comp
        fields = ('department', 'pc_name', 'disks', 'rams', 'monitors')

    def filter_by_online_date(self, queryset, name, value):
        if value is not None:
            return queryset.filter(online_date__lte=timezone.now()
                                   - timedelta(days=int(value)))
        return queryset

    def filter_lost_disks(self, queryset, name, value):
        if value:
            return queryset.filter(disks__status=ItemsChoices.LOST).distinct()
        return queryset

    def filter_lost_rams(self, queryset, name, value):
        if value:
            return queryset.filter(rams__status=ItemsChoices.LOST).distinct()
        return queryset

    def filter_lost_monitors(self, queryset, name, value):
        if value:
            return queryset.filter(
                monitors__status=ItemsChoices.LOST).distinct()
        return queryset


class DiskFilter(django_filters.FilterSet):
    department = django_filters.NumberFilter(method='filter_by_department')

    class Meta:
        model = Disk
        fields = ('department',)

    def filter_by_department(self, queryset, name, value):
        if value is not None:
            return queryset.filter(comp__department=value,
                                   status=ItemsChoices.INSTALLED)
        return queryset


class RamFilter(DiskFilter):
    class Meta:
        model = Ram
        fields = ('department',)


class MonitorFilter(DiskFilter):
    class Meta:
        model = Monitor
        fields = ('department',)
