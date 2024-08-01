import django_filters
from django.db.models import Q


class UsersFilter(django_filters.FilterSet):
    """Фильтр для поиска по учетным записям пользователей."""
    q = django_filters.CharFilter(
        method='filter_all_fields',
        label='Поиск по всем полям'
    )
    status = django_filters.CharFilter(field_name='status')
    rdlogin = django_filters.CharFilter(field_name='rdlogin__status')
    vpn = django_filters.CharFilter(field_name='vpn__status')
    gigro = django_filters.CharFilter(method='filter_gigro')

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

    def filter_gigro(self, queryset, name, value):
        if value:
            return queryset.filter(gigro__status=value).distinct()
        return queryset
