from services.models import RocketChat
from services.services import RocketChatService


def update_rocket():
    """Обновляет учетные записи RocketChat."""
    servers = RocketChat.objects.filter(active=True)
    service = RocketChatService()
    for server in servers:
        session = service.session(**server.credentials())
        service.block_users(session, server.need_disable)
