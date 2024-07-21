import json
import logging

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import status

from exceptions.services import MissingVariableError, RadiusUsersNotFoundError
from utils.utils import (check_envs, get_pages, read_ad_users,
                         read_radius_users, read_vpn_users, get_counters,
                         block_radius_users, block_vpn_users)

from .filters import UsersFilter
from .models import VPN, ADUsers, Radius
from .utils import (update_or_create_users,
                    match_vpn_users,
                    match_radius_users,
                    get_file)

logger = logging.getLogger(__name__)


def users_main(request):
    """Список всех учетных записей из AD."""
    ad_users = ADUsers.objects.all().select_related('rdlogin', 'vpn')
    related_statuses = ad_users.values('rdlogin__status', 'vpn__status')
    unrelated_radius_statuses = (Radius.objects
                                 .filter(ad_user__isnull=True)
                                 .values('status'))
    unrelated_vpn_statuses = (VPN.objects
                              .filter(ad_user__isnull=True)
                              .values('status'))

    ad_users_statuses = get_counters(ad_users.values('status'), 'status')
    radius_users_statuses = get_counters(related_statuses, 'rdlogin__status')
    vpn_users_statuses = get_counters(related_statuses, 'vpn__status')

    unrelated_radius_users_statuses = get_counters(
        unrelated_radius_statuses, 'status')
    unrelated_vpn_users_statuses = get_counters(
        unrelated_vpn_statuses, 'status')

    user_filter = UsersFilter(request.GET, queryset=ad_users)

    page_obj = get_pages(request, user_filter.qs)
    current_query_params = request.GET.copy()
    current_query_params.pop('page', None)

    context = {
        'page_obj': page_obj,
        'ad_users_statuses': ad_users_statuses,
        'radius_users_statuses': radius_users_statuses,
        'vpn_users_statuses': vpn_users_statuses,
        'unrelated_radius_users_statuses': unrelated_radius_users_statuses,
        'unrelated_vpn_users_statuses': unrelated_vpn_users_statuses,
        'current_query_params': current_query_params,
    }

    return render(request, 'users/users.html', context)


@csrf_exempt
def edit_user(request):
    """Редактирование связаных учетных записей пользователя."""
    if request.method == 'POST':
        ad_user_id = request.POST.get('ad_user_id')
        login_id = request.POST.get('rdlogin_id') or request.POST.get('vpn_id')
        field = request.POST.get('field')
        ad_user = ADUsers.objects.get(id=ad_user_id)
        setattr(ad_user, field, login_id)
        ad_user.save()
        return JsonResponse({'success': True}, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        body = json.loads(request.body.decode('utf-8'))
        ad_user_id = body.get('ad_user_id')
        ad_user = ADUsers.objects.get(id=ad_user_id)
        field = body.get('field')
        setattr(ad_user, field, None)
        ad_user.save()
        return JsonResponse({'success': True}, status=status.HTTP_200_OK)

    return JsonResponse({'success': False},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


def get_rdlogins(request):
    """Получить список доступных учетных записей Radius."""
    rdlogins = list(Radius.objects.filter(ad_user=None).values('id', 'login'))
    return JsonResponse(rdlogins, safe=False)


def get_vpns(request):
    """Получить список доступных учетных записей VPN."""
    vpns = list(VPN.objects.filter(ad_user=None).values('id', 'login'))
    return JsonResponse(vpns, safe=False)


def update_users_data(request):
    """Обновляет учетные данные из внешних систем.
    - Active Directory
    - WiFi Radius
    - VPN Mikrotik
    """
    try:
        # Проверяем необходимые перменные окружения
        ad_params = check_envs(settings.AD)
        vpn_params = check_envs(settings.VPN)
        radius_params = check_envs(settings.RADIUS)

        # Получем данные из систем
        ad_users = read_ad_users(ad_params)
        vpn_users = read_vpn_users(vpn_params)
        radius_users = read_radius_users(radius_params)

        # Обновляем пользователей в БД
        update_or_create_users(ADUsers, ad_users)
        update_or_create_users(VPN, vpn_users)
        update_or_create_users(Radius, radius_users)
        match_vpn_users()
        match_radius_users()

        # Отключить учетные записи в связных сервисах
        block_radius_users(radius_params)
        block_vpn_users(vpn_params)

    except (MissingVariableError, RadiusUsersNotFoundError) as error:
        logger.error(str(error))
        return JsonResponse(
            {'success': False, 'error': str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as error:
        logger.exception(f'Необработанная ошибка: {str(error)}')
        return JsonResponse(
            {'success': False, 'error': str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )
    return JsonResponse({'success': True}, status=status.HTTP_200_OK)


def generate_users_report(request):
    """Формирует список связных учетных записей, отдает файлом Excel."""
    users = ADUsers.objects.all().filter(
        Q(rdlogin__isnull=False) | Q(vpn__isnull=False)
        ).select_related('rdlogin', 'vpn')

    excel_file = get_file(users)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
    response['Content-Disposition'] = 'attachment; filename="users_report.xlsx"'  # noqa

    excel_file.save(response)

    return response
