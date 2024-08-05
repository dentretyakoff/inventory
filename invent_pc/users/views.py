import json
import logging

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework import status

from exceptions.services import MissingVariableError, RadiusUsersNotFoundError
from utils.utils import get_pages, get_counters

from .filters import UsersFilter
from .models import VPN, ADUsers, Radius
from .utils import get_file, get_radius_file, get_vpn_file
from .update_gigrotermon import update_gigrotermon
from .update_ad import update_ad
from .update_vpn import update_vpn
from .update_radius import update_radius

logger = logging.getLogger(__name__)


@login_required
def users_main(request):
    """Список всех учетных записей из AD."""
    ad_users = (ADUsers.objects.all()
                .select_related('rdlogin', 'vpn')
                .prefetch_related('gigro'))
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


@login_required
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


@login_required
def get_rdlogins(request):
    """Получить список доступных учетных записей Radius."""
    rdlogins = list(Radius.objects.filter(ad_user=None).values('id', 'login'))
    return JsonResponse(rdlogins, safe=False)


@login_required
def get_vpns(request):
    """Получить список доступных учетных записей VPN."""
    vpns = list(VPN.objects.filter(ad_user=None).values('id', 'login'))
    return JsonResponse(vpns, safe=False)


@login_required
def update_users_data(request):
    """Обновляет учетные данные из внешних систем.
    - Active Directory
    - WiFi Radius
    - VPN Mikrotik
    """
    try:
        # Обновление учетных записей
        update_ad()
        update_vpn()
        update_radius()
        update_gigrotermon()

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
    finally:
        ADUsers.clear_users_for_blocking()
        Radius.clear_users_for_blocking()
        VPN.clear_users_for_blocking()
    return JsonResponse({'success': True}, status=status.HTTP_200_OK)


@login_required
def generate_users_report(request):
    """Формирует список связных учетных записей, отдает файлом Excel."""
    users = ADUsers.objects.all().filter(
        Q(rdlogin__isnull=False) | Q(vpn__isnull=False)
        ).select_related('rdlogin', 'vpn')

    excel_file = get_file(users)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
    response['Content-Disposition'] = 'attachment; filename="ad_users_report.xlsx"'  # noqa

    excel_file.save(response)

    return response


@login_required
def generate_radius_report(request):
    """Формирует список свободных учетных запитсей Radius,
    отдает файлом Excel."""
    users = Radius.objects.filter(ad_user__isnull=True)

    excel_file = get_radius_file(users)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
    response['Content-Disposition'] = 'attachment; filename="radius_users_report.xlsx"'  # noqa

    excel_file.save(response)

    return response


@login_required
def generate_vpn_report(request):
    """Формирует список свободных учетных запитсей VPN,
    отдает файлом Excel."""
    users = VPN.objects.filter(ad_user__isnull=True)

    excel_file = get_vpn_file(users)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')  # noqa
    response['Content-Disposition'] = 'attachment; filename="vpn_users_report.xlsx"'  # noqa

    excel_file.save(response)

    return response
