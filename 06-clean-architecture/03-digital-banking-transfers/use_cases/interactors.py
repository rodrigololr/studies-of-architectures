"""
use_cases/interactors.py - Camada 2: Interactor de Transferências Bancárias.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from entities.models import Transfer, TransferMethod, TransferStatus
from use_cases.dto import TransferFundsRequestModel, TransferFundsResponseModel
from use_cases.boundaries import (
    TransferFundsInputBoundary,
    TransferFundsOutputBoundary,
    AccountRepositoryGateway,
    PixDirectoryGateway,
    TransferRepositoryGateway,
)


class TransferFundsInteractor(TransferFundsInputBoundary):
    def __init__(
        self,
        account_repo: AccountRepositoryGateway,
        pix_gateway: PixDirectoryGateway,
        transfer_repo: TransferRepositoryGateway,
        presenter: TransferFundsOutputBoundary,
    ) -> None:
        self.account_repo = account_repo
        self.pix_gateway = pix_gateway
        self.transfer_repo = transfer_repo
        self.presenter = presenter

    def execute(self, request: TransferFundsRequestModel) -> None:
        # 1. Busca Conta de Origem
        source_account = self.account_repo.find_by_account_number(request.from_account)
        if not source_account:
            self.presenter.present(TransferFundsResponseModel(
                success=False,
                transfer_id=None,
                from_account=request.from_account,
                to_account=request.destination_target,
                amount=request.amount,
                remaining_balance=None,
                timestamp=None,
                message=f"Conta de origem '{request.from_account}' não encontrada.",
            ))
            return

        # 2. Resolução da Conta de Destino (PIX DICT ou TED)
        method = TransferMethod.PIX if request.method.upper() == "PIX" else TransferMethod.TED
        dest_account_num = request.destination_target

        if method == TransferMethod.PIX:
            pix_record = self.pix_gateway.lookup_pix_key(request.destination_target)
            if pix_record:
                dest_account_num = pix_record.account_number
            else:
                # Se não for chave, verifica se é número direto de conta
                direct = self.account_repo.find_by_account_number(request.destination_target)
                if not direct:
                    self.presenter.present(TransferFundsResponseModel(
                        success=False,
                        transfer_id=None,
                        from_account=source_account.account_number,
                        to_account=request.destination_target,
                        amount=request.amount,
                        remaining_balance=source_account.balance,
                        timestamp=None,
                        message=f"Chave PIX ou conta '{request.destination_target}' não localizada no diretório Bacen.",
                    ))
                    return
                dest_account_num = direct.account_number

        dest_account = self.account_repo.find_by_account_number(dest_account_num)
        if not dest_account:
            self.presenter.present(TransferFundsResponseModel(
                success=False,
                transfer_id=None,
                from_account=source_account.account_number,
                to_account=dest_account_num,
                amount=request.amount,
                remaining_balance=source_account.balance,
                timestamp=None,
                message=f"Conta favorecida '{dest_account_num}' não encontrada.",
            ))
            return

        # 3. Não permite transferência para si mesmo
        if source_account.account_number == dest_account.account_number:
            self.presenter.present(TransferFundsResponseModel(
                success=False,
                transfer_id=None,
                from_account=source_account.account_number,
                to_account=dest_account_num,
                amount=request.amount,
                remaining_balance=source_account.balance,
                timestamp=None,
                message="Conta de origem e destino não podem ser idênticas.",
            ))
            return

        # 4. Avalia Invariantes de Negócio na Entidade (Saldo, Limite Noturno, Bloqueio)
        is_allowed, denial_reason = source_account.check_transfer_eligibility(
            request.amount,
            request.is_night_time,
        )

        now = datetime.now(timezone.utc)
        transfer_id = f"tx_{uuid.uuid4().hex[:10]}"

        if not is_allowed:
            failed_tx = Transfer(
                transfer_id=transfer_id,
                from_account_number=source_account.account_number,
                to_account_number=dest_account.account_number,
                amount=request.amount,
                method=method,
                status=TransferStatus.FAILED,
                transacted_at=now,
                error_reason=denial_reason,
            )
            self.transfer_repo.save(failed_tx)
            self.presenter.present(TransferFundsResponseModel(
                success=False,
                transfer_id=transfer_id,
                from_account=source_account.account_number,
                to_account=dest_account.account_number,
                amount=request.amount,
                remaining_balance=source_account.balance,
                timestamp=now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                message=denial_reason or "Transferência recusada por política bancária.",
            ))
            return

        # 5. Execução do Débito e Crédito Atômicos
        source_account.debit(request.amount)
        dest_account.credit(request.amount)

        self.account_repo.save(source_account)
        self.account_repo.save(dest_account)

        completed_tx = Transfer(
            transfer_id=transfer_id,
            from_account_number=source_account.account_number,
            to_account_number=dest_account.account_number,
            amount=request.amount,
            method=method,
            status=TransferStatus.COMPLETED,
            transacted_at=now,
        )
        self.transfer_repo.save(completed_tx)

        # 6. Emissão para Apresentador (Output Boundary)
        self.presenter.present(TransferFundsResponseModel(
            success=True,
            transfer_id=transfer_id,
            from_account=source_account.account_number,
            to_account=dest_account.account_number,
            amount=request.amount,
            remaining_balance=source_account.balance,
            timestamp=now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            message=f"Transferência {method.value} realizada com sucesso!",
        ))
