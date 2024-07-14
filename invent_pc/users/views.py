import json
import logging
from collections import Counter

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from exceptions.services import MissingVariableError, RadiusUsersNotFoundError
from rest_framework import status
from utils.utils import (check_envs, get_pages, read_ad_users,
                         read_radius_users, read_vpn_users)

from .filters import UsersFilter
from .models import VPN, ADUsers, Radius
from .utils import update_or_create_users

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

    ad_users_statuses = dict(Counter(
        status['status'] for status in ad_users.values('status'))
    )
    radius_users_statuses = dict(Counter(
        status['rdlogin__status']
        for status in related_statuses if status['rdlogin__status'])
    )
    vpn_users_statuses = dict(Counter(
        status['vpn__status']
        for status in related_statuses if status['vpn__status'])
    )
    unrelated_radius_users_statuses = dict(Counter(
        status['status'] for status in unrelated_radius_statuses)
    )
    unrelated_vpn_users_statuses = dict(Counter(
        status['status'] for status in unrelated_vpn_statuses)
    )

    ad_users_statuses['total'] = (sum(ad_users_statuses.values()))
    radius_users_statuses['total'] = (sum(radius_users_statuses.values()))
    vpn_users_statuses['total'] = (sum(vpn_users_statuses.values()))
    unrelated_radius_users_statuses['total'] = (sum(
        unrelated_radius_users_statuses.values()))
    unrelated_vpn_users_statuses['total'] = (sum(
        unrelated_vpn_users_statuses.values()))

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
