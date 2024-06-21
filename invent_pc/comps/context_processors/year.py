import datetime as dt


def year(request):
    """Добавляет переменную в контекст с текущим годом."""
    year = dt.date.today().year
    return {
        'year': year
    }
