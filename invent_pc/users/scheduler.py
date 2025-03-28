import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model

from .views import update_users_data


logger = logging.getLogger(__name__)


def update_users_data_task():
    logger.info('Выполняю задачу обновления учетных записей')
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        logger.error('Нет суперпользователя, не могу выполнить задачу')
        return

    factory = RequestFactory()
    request = factory.get('/fake-path/')
    request.user = user
    update_users_data(request)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_users_data_task,
        trigger=IntervalTrigger(seconds=settings.SCHEDULER_INTERVAL))
    scheduler.start()
