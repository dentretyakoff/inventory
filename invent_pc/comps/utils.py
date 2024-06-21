from django.conf import settings
from django.core.paginator import Paginator

COUNT_PAGES = settings.COUNT_PAGES_PAGINATOR


# Паджинация
def get_pages(request, comps, count_pages=COUNT_PAGES):
    paginator = Paginator(comps, count_pages)
    page_number = request.GET.get('page')

    # Возвращаем набор записей для страницы с запрошенным номером
    return paginator.get_page(page_number)
