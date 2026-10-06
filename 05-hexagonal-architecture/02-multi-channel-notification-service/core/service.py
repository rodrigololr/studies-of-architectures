"""
service.py - Núcleo da Aplicação (Core) para Despacho de Notificações.

Implementa `SendNotificationUseCasePort` sem acoplamento a serviços de mensageria concretos.
"""

from __future__ import annotations
from typing import Dict, List
from datetime import datetime, timezone
from domain.models import (
    NotificationMessage,
    DispatchResult,
    DispatchStatus,
    ChannelType,
    NotificationPriority,
)
from domain.exceptions import (
    InvalidRecipientException,
    AllChannelsExhaustedException,
)
from ports.driver import SendNotificationUseCasePort
from ports.driven import (
    NotificationChannelPort,
    TemplateEnginePort,
    NotificationHistoryRepositoryPort,
)


class NotificationDispatcherService(SendNotificationUseCasePort):
    def __init__(
        self,
        channels: Dict[ChannelType, NotificationChannelPort],
        template_engine: TemplateEnginePort,
        history_repo: NotificationHistoryRepositoryPort,
    ) -> None:
        self._channels = channels
        self._template_engine = template_engine
        self._history_repo = history_repo

    def dispatch(self, message: NotificationMessage) -> DispatchResult:
        # 1. Validação de dados do destinatário
        if not message.recipient.email and not message.recipient.phone_number:
            raise InvalidRecipientException("Destinatário precisa ter ao menos e-mail ou telefone cadastrado.")

        # 2. Renderização do template via Driven Port
        rendered_content = self._template_engine.render(
            message.template_name,
            {"name": message.recipient.name, **message.template_params},
        )

        # 3. Determinação da ordem dos canais
        # Se mensagem define preferências explícitas, usa-as; caso contrário, usa a prioridade do negócio
        candidate_channels = list(message.preferred_channels)
        if not candidate_channels:
            if message.priority == NotificationPriority.CRITICAL_2FA:
                candidate_channels = [ChannelType.WHATSAPP, ChannelType.SMS, ChannelType.EMAIL]
            elif message.priority == NotificationPriority.MEDIUM:
                candidate_channels = [ChannelType.EMAIL, ChannelType.WHATSAPP]
            else:
                candidate_channels = [ChannelType.EMAIL]

        # 4. Tentativa de entrega através dos canais com fallback
        attempted_errors: List[str] = []
        for index, channel_type in enumerate(candidate_channels):
            channel_adapter = self._channels.get(channel_type)
            if not channel_adapter:
                attempted_errors.append(f"Canal {channel_type.value} não registrado no sistema")
                continue

            if not channel_adapter.is_healthy():
                attempted_errors.append(f"Canal {channel_type.value} está temporariamente inoperante")
                continue

            try:
                success = channel_adapter.send(message.recipient, rendered_content)
                if success:
                    # Se não for o primeiro canal, foi entregue via fallback
                    status = DispatchStatus.DELIVERED if index == 0 else DispatchStatus.FALLBACK_DELIVERED
                    result = DispatchResult(
                        message_id=message.message_id,
                        recipient_user_id=message.recipient.user_id,
                        channel_used=channel_type,
                        status=status,
                        content_rendered=rendered_content,
                        dispatched_at=datetime.now(timezone.utc),
                    )
                    self._history_repo.record_dispatch(result)
                    return result
                else:
                    attempted_errors.append(f"Canal {channel_type.value} rejeitou a entrega da mensagem")
            except Exception as err:
                attempted_errors.append(f"Canal {channel_type.value} falhou: {str(err)}")

        # 5. Se todos os canais falharam
        all_errs = "; ".join(attempted_errors)
        failed_result = DispatchResult(
            message_id=message.message_id,
            recipient_user_id=message.recipient.user_id,
            channel_used=candidate_channels[0] if candidate_channels else ChannelType.EMAIL,
            status=DispatchStatus.FAILED,
            content_rendered=rendered_content,
            dispatched_at=datetime.now(timezone.utc),
            error_details=all_errs,
        )
        self._history_repo.record_dispatch(failed_result)
        raise AllChannelsExhaustedException(f"Todos os canais de envio falharam: [{all_errs}]")
