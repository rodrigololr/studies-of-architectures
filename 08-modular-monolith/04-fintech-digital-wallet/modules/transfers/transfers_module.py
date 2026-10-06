"""Ponto de Entrada e Facade do Módulo Transfers."""

import uuid
from shared.events import InProcessEventBus
from modules.accounts.public_contracts import (
    IAccountsModule,
    DebitAccountCommand,
    CreditAccountCommand,
    InsufficientFundsError,
)
from modules.compliance.public_contracts import (
    IComplianceModule,
    ComplianceCheckRequestDto,
)
from modules.transfers.public_contracts import (
    ITransfersModule,
    ExecutePixTransferCommand,
    TransferResultDto,
    TransferCompletedDomainEvent,
    TransferRejectedDomainEvent,
)
from modules.transfers.internal.transfers_internal import (
    _InternalTransfer,
    _InternalTransfersRepository,
)


class TransfersModule(ITransfersModule):
    """Facade do módulo Transfers.
    
    Orquestra a liquidação de PIX coordenando Accounts e Compliance.
    """
    def __init__(
        self,
        accounts_module: IAccountsModule,
        compliance_module: IComplianceModule,
        event_bus: InProcessEventBus,
    ) -> None:
        self._accounts = accounts_module
        self._compliance = compliance_module
        self._bus = event_bus
        self._repo = _InternalTransfersRepository()

    def execute_pix_transfer(self, cmd: ExecutePixTransferCommand) -> TransferResultDto:
        transfer_id = f"PIX_{uuid.uuid4().hex[:8].upper()}"

        # 1. Verifica conta de origem
        origin = self._accounts.get_account(cmd.origin_account_id)
        if not origin or not origin.is_active:
            return TransferResultDto(
                transfer_id=transfer_id,
                origin_account_id=cmd.origin_account_id,
                destination_pix_key=cmd.destination_pix_key,
                amount=cmd.amount,
                status="ORIGIN_NOT_FOUND",
                authorization_code=None,
                message="Conta pagadora não localizada ou inativa.",
            )

        # 2. Avaliação de Risco e Compliance (PLD / Sanções)
        compliance_check = self._compliance.evaluate_transfer(ComplianceCheckRequestDto(
            origin_account_id=origin.account_id,
            origin_cpf=origin.cpf,
            destination_pix_key=cmd.destination_pix_key,
            amount=cmd.amount,
        ))

        if not compliance_check.is_approved:
            self._bus.publish(TransferRejectedDomainEvent(
                origin_account_id=cmd.origin_account_id,
                destination_pix_key=cmd.destination_pix_key,
                amount=cmd.amount,
                reason=compliance_check.reason,
            ))
            return TransferResultDto(
                transfer_id=transfer_id,
                origin_account_id=cmd.origin_account_id,
                destination_pix_key=cmd.destination_pix_key,
                amount=cmd.amount,
                status="REJECTED_COMPLIANCE",
                authorization_code=None,
                message=compliance_check.reason,
            )

        # 3. Resolução da Chave PIX de Destino
        dest = self._accounts.get_by_pix_key(cmd.destination_pix_key)
        if not dest or not dest.is_active:
            return TransferResultDto(
                transfer_id=transfer_id,
                origin_account_id=cmd.origin_account_id,
                destination_pix_key=cmd.destination_pix_key,
                amount=cmd.amount,
                status="DESTINATION_NOT_FOUND",
                authorization_code=None,
                message=f"Chave PIX '{cmd.destination_pix_key}' não encontrada no DICT/banco.",
            )

        # 4. Débito Atômico na Origem
        try:
            self._accounts.debit(DebitAccountCommand(
                account_id=origin.account_id,
                amount=cmd.amount,
                description=f"PIX enviado para {dest.owner_name}",
            ))
        except InsufficientFundsError as e:
            return TransferResultDto(
                transfer_id=transfer_id,
                origin_account_id=cmd.origin_account_id,
                destination_pix_key=cmd.destination_pix_key,
                amount=cmd.amount,
                status="FAILED_INSUFFICIENT_FUNDS",
                authorization_code=None,
                message=str(e),
            )

        # 5. Crédito Atômico no Destino
        self._accounts.credit(CreditAccountCommand(
            account_id=dest.account_id,
            amount=cmd.amount,
            description=f"PIX recebido de {origin.owner_name}",
        ))

        auth_code = f"E{uuid.uuid4().hex[:12].upper()}"
        tx_record = _InternalTransfer(
            transfer_id=transfer_id,
            origin_account_id=origin.account_id,
            destination_pix_key=cmd.destination_pix_key,
            amount=cmd.amount,
            status="COMPLETED",
            authorization_code=auth_code,
        )
        self._repo.save(tx_record)

        # 6. Emissão de evento de transferência concluída
        self._bus.publish(TransferCompletedDomainEvent(
            transfer_id=transfer_id,
            origin_account_id=origin.account_id,
            destination_pix_key=cmd.destination_pix_key,
            amount=cmd.amount,
        ))

        return TransferResultDto(
            transfer_id=transfer_id,
            origin_account_id=origin.account_id,
            destination_pix_key=cmd.destination_pix_key,
            amount=cmd.amount,
            status="COMPLETED",
            authorization_code=auth_code,
            message=f"Transferência PIX concluída com sucesso para {dest.owner_name}.",
        )
