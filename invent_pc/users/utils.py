import openpyxl
from django.db.models import Model

from .models import ADUsers, Radius, VPN, StatusChoices


def update_or_create_users(
        model: Model, users_data: list[dict[str, str]]) -> None:
    """Обновляет пользователей или создает новых."""
    existing_users = model.objects.in_bulk(field_name='login')
    new_users = []

    for user_data in users_data:
        login = user_data.pop('login')
        user = existing_users.pop(login, None)
        user_data['successfully_updated'] = True
        if not user:
            new_users.append(model(login=login, **user_data))
        elif user.needs_update(user_data):
            user.save()

    if existing_users:
        for existing_user in existing_users.values():
            existing_user.successfully_updated = False
        model.objects.bulk_update(existing_users.values(),
                                  ['successfully_updated'])

    if new_users:
        model.objects.bulk_create(new_users)


def make_clean_wb(title: str, headers: list[str]) -> openpyxl.Workbook:
    """Формирует чистую книгу Excel."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title
    ws.append(headers)

    for cell in ws['1:1']:
        cell.font = openpyxl.styles.Font(bold=True)
        cell.fill = openpyxl.styles.PatternFill('solid', fgColor='00C0C0C0')

    return wb


def get_file(users: ADUsers) -> openpyxl.Workbook:
    """Создает Excel со связными учетными записями."""
    title = 'Список учетных записей'
    headers = ['№', 'ФИО', 'Логин', 'Email',
               'Wi-Fi', 'VPN логин', 'VPN комментарий']
    wb = make_clean_wb(title, headers)
    ws = wb.active

    for num, user in enumerate(users, 1):
        ws.append([
            num,
            user.fio,
            user.login,
            user.email,
            getattr(user.rdlogin, 'login', '-'),
            getattr(user.vpn, 'login', '-'),
            getattr(user.vpn, 'comment', '-')
        ])

        statuses = {
            # ws.cell(row= , column=)
            ws.cell(num+1, 3): getattr(user, 'status', None),
            ws.cell(num+1, 5): getattr(user.rdlogin, 'status', None),
            ws.cell(num+1, 6): getattr(user.vpn, 'status', None)
        }
        for cell, status in statuses.items():
            if status == StatusChoices.INACTIVE:
                cell.fill = openpyxl.styles.PatternFill(
                    'solid', fgColor='FF0000')  # Красный

    return wb


def get_radius_file(users: Radius) -> openpyxl.Workbook:
    """Создает Excel со свободными учетными записями Radius."""
    title = 'Список учетных записей'
    headers = ['№', 'ФИО', 'Логин']
    wb = make_clean_wb(title, headers)
    ws = wb.active

    for num, user in enumerate(users, 1):
        ws.append([num, user.fio, user.login])
        if user.status == StatusChoices.INACTIVE:
            ws.cell(num+1, 3).fill = openpyxl.styles.PatternFill(
                'solid', fgColor='FF0000')  # Красный

    return wb


def get_vpn_file(users: VPN) -> openpyxl.Workbook:
    """Создает Excel со свободными учетными записями VPN."""
    title = 'Список учетных записей'
    headers = ['№', 'Логин', 'Комментарий']
    wb = make_clean_wb(title, headers)
    ws = wb.active

    for num, user in enumerate(users, 1):
        ws.append([num, user.login, user.comment])
        if user.status == StatusChoices.INACTIVE:
            ws.cell(num+1, 2).fill = openpyxl.styles.PatternFill(
                'solid', fgColor='FF0000')  # Красный

    return wb
