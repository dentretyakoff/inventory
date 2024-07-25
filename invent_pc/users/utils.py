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
        user = existing_users.get(login)
        if not user:
            new_users.append(model(login=login, **user_data))
        elif user.needs_update(user_data):
            user.save()

    if new_users:
        model.objects.bulk_create(new_users)


def match_vpn_users() -> None:
    """Сопоставляет VPN с учетными записями AD."""
    no_vpn_users = ADUsers.objects.filter(vpn=None)
    vpn_users = {
        user.comment.lower(): user
        for user in VPN.objects.filter(
            ad_user__isnull=True,
            comment__isnull=False
        )
    }

    updated_users = []

    for no_vpn_user in no_vpn_users:
        for comment, vpn_user in vpn_users.items():
            if no_vpn_user.fio and no_vpn_user.fio.lower() in comment:
                no_vpn_user.vpn = vpn_user
                updated_users.append(no_vpn_user)

    ADUsers.objects.bulk_update(updated_users, ('vpn',))


def match_radius_users() -> None:
    """Сопоставляет Radius с учетными записями AD."""
    no_radius_users = ADUsers.objects.filter(rdlogin=None)
    radius_users = Radius.objects.filter(
        ad_user__isnull=True,
        fio__isnull=False
    )

    updated_users = []

    for no_radius_user in no_radius_users:
        for radius_user in radius_users:
            if (no_radius_user.fio == radius_user.fio
                    or no_radius_user.login == radius_user.login):
                no_radius_user.rdlogin = radius_user
                updated_users.append(no_radius_user)

    ADUsers.objects.bulk_update(updated_users, ('rdlogin',))


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
            ws.cell(num, 3).fill = openpyxl.styles.PatternFill(
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
            ws.cell(num, 2).fill = openpyxl.styles.PatternFill(
                'solid', fgColor='FF0000')  # Красный

    return wb
