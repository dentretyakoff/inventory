import django_filters
from django.db.models import Q


class BaseFilter(django_filters.FilterSet):
    """Базовый фильтр учетных записей."""
    q = django_filters.CharFilter(
        method='filter_all_fields',
        label='Поиск по всем полям'
    )
    status = django_filters.CharFilter(field_name='status')

    def filter_all_fields(self, queryset, name, value):
        if value:
            return queryset.filter(login__icontains=value)
        return queryset


class UsersFilter(BaseFilter):
    """Фильтр по учетным записям AD."""
    rdlogin = django_filters.CharFilter(field_name='rdlogin__status')
    vpn = django_filters.CharFilter(field_name='vpn__status')
    gigro = django_filters.CharFilter(method='filter_gigro')
    email = django_filters.BooleanFilter(
        field_name='email', method='filter_email')

    def filter_all_fields(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(fio__icontains=value) |
                Q(login__icontains=value) |
                Q(email__icontains=value) |
                Q(rdlogin__login__icontains=value) |
                Q(vpn__login__icontains=value)
            )
        return queryset

    def filter_email(self, queryset, name, value):
        if value:
            return queryset.filter(email__isnull=False)
        return queryset

    def filter_gigro(self, queryset, name, value):
        if value:
            return queryset.filter(gigro__status=value).distinct()
        return queryset


class RadiusUsersFilter(BaseFilter):
    """Фильтр по учетным записям Radius."""
    def filter_all_fields(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(fio__icontains=value) | Q(login__icontains=value)
            )
        return queryset


class VPNUsersFilter(BaseFilter):
    """Фильтр по учетным записям VPN."""
    def filter_all_fields(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(comment__icontains=value) | Q(login__icontains=value)
            )
        return queryset


class GigroUsersFilter(BaseFilter):
    """Фильтр по учетным записям Гигротермон."""
    def filter_all_fields(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(login__icontains=value) |
                Q(db__name__icontains=value) |
                Q(ad_user__fio__icontains=value)
            )
        return queryset
