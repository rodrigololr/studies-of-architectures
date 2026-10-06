"""Ponto de Entrada e Facade do Módulo Notifications."""

import uuid
from typing import List
from shared.events import InProcessEventBus
from modules.transfers.public_contracts import (
    TransferCompletedDomainEvent,
    TransferRejectedDomainEvent,
)
from modules.notifications.public_contracts import (
    INotificationsModule,
    NotificationDto,
)
from modules.notifications.internal.notifications_internal import (
    _InternalNotification,
    _InternalNotificationRepository,
)


class NotificationsModule(INotificationsModule):
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._bus = event_bus
        self._repo = _InternalNotificationRepository()

        # Inscrição para eventos de transferência
        self._bus.subscribe(TransferCompletedDomainEvent, self._handle_transfer_completed)
        self._bus.subscribe(TransferRejectedDomainEvent, self._handle_transfer_rejected)

    def _handle_transfer_completed(self, e: TransferCompletedDomainEvent) -> None:
        self._repo.save(_InternalNotification(
            notification_id=f"NOT_{uuid.uuid4().hex[:8].upper()}",
            recipient_id=e.origin_account_id,
            channel="PUSH",
            message=f"PIX enviado com sucesso no valor de R$ {e.amount:,.2f} para chave '{e.destination_pix_key}'.",
        ))

    def _handle_transfer_rejected(self, e: TransferRejectedDomainEvent) -> None:
        self._repo.save(_InternalNotification(
            notification_id=f"NOT_{uuid.uuid4().hex[:8].upper()}",
            recipient_id=e.origin_account_id,
            channel="SMS",
            message=f"Alerta de Segurança: Transferência de R$ {e.amount:,.2f} não realizada. {e.reason}",
        ))

    def list_notifications(self, recipient_id: str) -> List[NotificationDto]:
        return [
            NotificationDto(
                notification_id=n.notification_id,
                recipient_id=n.recipient_id,
                channel=n.channel,
                message=n.message,
                sent_at=n.sent_at,
            )
            for n in self._repo.list_by_recipient(recipient_id)
        ]

    def list_all(self) -> List[NotificationDto]:
        return [
            NotificationDto(
                notification_id=n.notification_id,
                recipient_id=n.recipient_id,
                channel=n.channel,
                message=n.message,
                sent_at=n.sent_at,
            )
            for n in self._repo.list_all()
        ]
