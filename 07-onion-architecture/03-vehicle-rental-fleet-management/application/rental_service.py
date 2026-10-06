"""
application/rental_service.py - Camada 3: Application Service.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.model.inspection import InspectionReport
from domain.model.contract import RentalContract, ContractStatus
from domain.services.penalty_calculator import RentalPenaltyAndFuelPolicyService
from application.interfaces import (
    IVehicleRepository,
    IRentalContractRepository,
    IPaymentSettlementGateway,
)
from application.dto import (
    OpenRentalCommand,
    OpenRentalResponseDto,
    CloseRentalCommand,
    CloseRentalResponseDto,
)


class RentalFleetApplicationService:
    def __init__(
        self,
        vehicle_repo: IVehicleRepository,
        contract_repo: IRentalContractRepository,
        payment_gateway: IPaymentSettlementGateway,
    ) -> None:
        self.vehicle_repo = vehicle_repo
        self.contract_repo = contract_repo
        self.payment_gateway = payment_gateway

    def open_rental(self, command: OpenRentalCommand) -> OpenRentalResponseDto:
        # 1. Localiza e valida disponibilidade do veículo
        vehicle = self.vehicle_repo.find_by_id(command.vehicle_id)
        if not vehicle:
            return OpenRentalResponseDto(
                success=False,
                contract_id=None,
                customer_name=command.customer_name,
                vehicle_model=None,
                days=command.rental_days,
                base_charge=0.0,
                message=f"Veículo '{command.vehicle_id}' não encontrado.",
            )

        if not vehicle.is_available():
            return OpenRentalResponseDto(
                success=False,
                contract_id=None,
                customer_name=command.customer_name,
                vehicle_model=vehicle.model_name,
                days=command.rental_days,
                base_charge=0.0,
                message=f"Veículo '{vehicle.model_name}' indisponível para locação (Status: {vehicle.status.value}).",
            )

        # 2. Vistoria Inicial (Saída do Pátio)
        checkout_report = InspectionReport(
            odometer_km=vehicle.current_odometer_km,
            fuel_level_eighths=vehicle.current_fuel_eighths,
            damages=[],
        )

        base_charge = round(vehicle.daily_rate * command.rental_days, 2)
        paid = self.payment_gateway.process_charge(
            customer_name=command.customer_name,
            amount=base_charge,
            description=f"Diárias Locação {vehicle.model_name} ({command.rental_days} dias)",
        )
        if not paid:
            return OpenRentalResponseDto(
                success=False,
                contract_id=None,
                customer_name=command.customer_name,
                vehicle_model=vehicle.model_name,
                days=command.rental_days,
                base_charge=base_charge,
                message="Falha no pagamento da caução/diárias iniciais.",
            )

        # 3. Cria Contrato e Bloqueia Veículo
        contract_id = f"LOC_{uuid.uuid4().hex[:8].upper()}"
        contract = RentalContract(
            contract_id=contract_id,
            customer_name=command.customer_name,
            vehicle=vehicle,
            rental_days=command.rental_days,
            checkout_inspection=checkout_report,
            base_charge=base_charge,
        )
        vehicle.mark_rented()

        # 4. Persiste
        self.vehicle_repo.save(vehicle)
        self.contract_repo.save(contract)

        return OpenRentalResponseDto(
            success=True,
            contract_id=contract_id,
            customer_name=command.customer_name,
            vehicle_model=vehicle.model_name,
            days=command.rental_days,
            base_charge=base_charge,
            message="Contrato de locação aberto com sucesso!",
        )

    def close_rental(self, command: CloseRentalCommand) -> CloseRentalResponseDto:
        # 1. Localiza Contrato
        contract = self.contract_repo.find_by_id(command.contract_id)
        if not contract:
            return CloseRentalResponseDto(
                success=False,
                contract_id=command.contract_id,
                base_charge=0.0,
                extra_fees=0.0,
                fee_breakdown={},
                total_charged=0.0,
                message=f"Contrato '{command.contract_id}' inexistente.",
            )

        if contract.status == ContractStatus.CLOSED:
            return CloseRentalResponseDto(
                success=False,
                contract_id=contract.contract_id,
                base_charge=contract.base_charge,
                extra_fees=contract.extra_fees,
                fee_breakdown={},
                total_charged=contract.total_charged,
                message="Este contrato já se encontra encerrado.",
            )

        # 2. Vistoria Final (Entrada no Pátio)
        checkin_report = InspectionReport(
            odometer_km=command.return_odometer_km,
            fuel_level_eighths=command.return_fuel_eighths,
            damages=command.damages,
        )

        # 3. Invocação do Domain Service para apuração de multas e custos
        extras, breakdown = RentalPenaltyAndFuelPolicyService.calculate_checkin_penalties(
            checkout=contract.checkout_inspection,
            checkin=checkin_report,
            rental_days=contract.rental_days,
        )

        # 4. Cobrança de custos adicionais se houver
        if extras > 0:
            self.payment_gateway.process_charge(
                customer_name=contract.customer_name,
                amount=extras,
                description=f"Taxas extras de encerramento de locação ({contract.contract_id})",
            )

        # 5. Encerramento do Contrato e Devolução do Veículo
        contract.close_contract(checkin_report, extras)
        self.contract_repo.save(contract)
        self.vehicle_repo.save(contract.vehicle)

        return CloseRentalResponseDto(
            success=True,
            contract_id=contract.contract_id,
            base_charge=contract.base_charge,
            extra_fees=extras,
            fee_breakdown=breakdown,
            total_charged=contract.total_charged,
            message="Locação encerrada e vistoria processada com sucesso!",
        )
