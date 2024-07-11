import django_filters
from django.db.models import Q


class UsersFilter(django_filters.FilterSet):
    """Фильтр для поиска по учетным записям пользователей."""
    q = django_filters.CharFilter(
        method='filter_all_fields',
        label='Поиск по всем полям'
    )

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
