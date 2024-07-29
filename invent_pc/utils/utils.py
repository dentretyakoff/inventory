from collections import Counter

from django.db.models import QuerySet
from django.conf import settings
from django.core.paginator import Paginator

from exceptions.services import MissingVariableError


COUNT_PAGES = settings.COUNT_PAGES_PAGINATOR


# Паджинация
def get_pages(request, queryset, count_pages=COUNT_PAGES):
    paginator = Paginator(queryset, count_pages)
    page_number = request.GET.get('page')

    # Возвращаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)


def check_envs(envs: dict) -> dict:
    """Проверяет переменные окружения."""
    for key, env in envs.items():
        if env in (None, ''):
            raise MissingVariableError(
                f'Некорректно заполнена переменная окружения: {key}')
    return envs


def get_counters(queryset: QuerySet, field: str) -> dict[str, str]:
    """Подсчитывает одинаковые элементы и их общее количество
    по определенному полю в queryset.
    """
    result = dict(Counter(item[field] for item in queryset if item[field]))
    result['total'] = sum(result.values())

    return result


def sorted_list(unsorted: dict[str, str]) -> list[str]:
    """Получает словарь возвращает отсортированный по значениям список."""
    return sorted(unsorted.items(), key=lambda item: item[1], reverse=True)
