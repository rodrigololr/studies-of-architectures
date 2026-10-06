"""
service.py - Camada de Negócio (Business Layer).

Responsável por:
- Cadastrar produtos no armazém.
- Registrar entradas de estoque com acréscimo de saldo disponível.
- Reservar itens para pedidos pendentes.
- Expedir/despachar itens reservados ou diretos.
- Detectar violação do ponto crítico de reposição (Reorder Point Alert).
"""

from __future__ import annotations
from datetime import datetime
import uuid
from typing import Dict, Tuple
from business.exceptions import (
    ProductNotFoundException,
    InsufficientStockException,
    InvalidStockOperationException,
)
from data.models import ProductStockModel, StockMovementModel, MovementType
from data.repository import InventoryRepository, StockMovementRepository


class InventoryService:
    def __init__(
        self,
        inventory_repo: InventoryRepository,
        movement_repo: StockMovementRepository,
    ) -> None:
        self.inventory_repo = inventory_repo
        self.movement_repo = movement_repo

    def register_product(
        self, sku: str, product_name: str, initial_qty: int, reorder_point: int
    ) -> ProductStockModel:
        if initial_qty < 0 or reorder_point < 0:
            raise InvalidStockOperationException("Quantidades e ponto de reposição não podem ser negativos.")

        stock = ProductStockModel(
            product_id=str(uuid.uuid4())[:8],
            sku=sku.strip().upper(),
            product_name=product_name.strip(),
            available_qty=initial_qty,
            reserved_qty=0,
            reorder_point=reorder_point,
        )
        self.inventory_repo.save(stock)

        if initial_qty > 0:
            self._record_movement(
                stock.product_id, MovementType.INBOUND, initial_qty, stock.available_qty, "Estoque inicial de abertura"
            )

        return stock

    def inbound_stock(self, product_id: str, quantity: int, invoice_number: str) -> ProductStockModel:
        if quantity <= 0:
            raise InvalidStockOperationException("A quantidade de entrada deve ser maior que zero.")

        stock = self._get_product_or_fail(product_id)
        stock.available_qty += quantity
        self.inventory_repo.save(stock)

        self._record_movement(
            product_id, MovementType.INBOUND, quantity, stock.available_qty, f"Entrada NF: {invoice_number}"
        )
        return stock

    def reserve_stock(self, product_id: str, quantity: int, order_id: str) -> ProductStockModel:
        if quantity <= 0:
            raise InvalidStockOperationException("Quantidade de reserva deve ser maior que zero.")

        stock = self._get_product_or_fail(product_id)
        if stock.available_qty < quantity:
            raise InsufficientStockException(
                f"Estoque livre insuficiente para reservar {quantity} un do SKU '{stock.sku}'. Livre: {stock.available_qty}."
            )

        stock.available_qty -= quantity
        stock.reserved_qty += quantity
        self.inventory_repo.save(stock)

        self._record_movement(
            product_id, MovementType.RESERVE, quantity, stock.available_qty, f"Reserva para Pedido #{order_id}"
        )
        return stock

    def dispatch_reserved_stock(
        self, product_id: str, quantity: int, order_id: str
    ) -> Tuple[ProductStockModel, bool]:
        """
        Expede mercadoria previamente reservada.
        Retorna (stock, reorder_alert_triggered).
        """
        if quantity <= 0:
            raise InvalidStockOperationException("Quantidade para expedição deve ser positiva.")

        stock = self._get_product_or_fail(product_id)
        if stock.reserved_qty < quantity:
            raise InsufficientStockException(
                f"Não há quantidade reservada suficiente ({stock.reserved_qty}) para expedir {quantity} un."
            )

        stock.reserved_qty -= quantity
        self.inventory_repo.save(stock)

        self._record_movement(
            product_id, MovementType.DISPATCH, quantity, stock.total_physical_qty, f"Despacho físico do Pedido #{order_id}"
        )

        # Checagem de Ponto de Reposição Crítico
        reorder_alert = stock.total_physical_qty <= stock.reorder_point
        return stock, reorder_alert

    def _get_product_or_fail(self, product_id: str) -> ProductStockModel:
        stock = self.inventory_repo.find_by_id(product_id)
        if not stock:
            raise ProductNotFoundException(f"Produto com ID '{product_id}' não encontrado no inventário.")
        return stock

    def _record_movement(
        self, product_id: str, mtype: MovementType, qty: int, balance_after: int, reason: str
    ) -> None:
        mv = StockMovementModel(
            movement_id=str(uuid.uuid4())[:8],
            product_id=product_id,
            movement_type=mtype,
            quantity=qty,
            balance_after=balance_after,
            reason=reason,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.movement_repo.record(mv)
