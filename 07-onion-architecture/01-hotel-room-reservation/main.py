"""
main.py - Camada 4: Infrastructure (Composition Root da Onion Architecture).
"""

import sys
import json
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from domain.model.room import Room, RoomCategory
from infrastructure.repositories import InMemoryRoomRepository, InMemoryReservationRepository
from infrastructure.payment_gateway import MockStripePaymentService
from infrastructure.web_controller import HotelReservationController
from application.booking_service import HotelBookingApplicationService


def main() -> None:
    print("=" * 80)
    print(" ONION ARCHITECTURE - EXEMPLO 01: HOTEL ROOM RESERVATION")
    print("=" * 80)

    # 1. Montagem da Infraestrutura (Casca da Cebola)
    room_repo = InMemoryRoomRepository({
        "101": Room("101", RoomCategory.STANDARD, base_daily_rate=200.0, max_occupancy=2),
        "201": Room("201", RoomCategory.DELUXE, base_daily_rate=450.0, max_occupancy=3),
        "301": Room("301", RoomCategory.PRESIDENTIAL, base_daily_rate=1200.0, max_occupancy=4),
    })
    res_repo = InMemoryReservationRepository()
    payment_service = MockStripePaymentService()

    # 2. Montagem da Aplicação (Camada 3)
    app_service = HotelBookingApplicationService(
        room_repo=room_repo,
        reservation_repo=res_repo,
        payment_service=payment_service,
    )

    # 3. Montagem do Controlador (UI / Camada 4)
    controller = HotelReservationController(booking_service=app_service)

    print("\n--- CENÁRIO 1: Reserva em Baixa Temporada (Dias Úteis de Outubro) ---")
    status, res = controller.handle_post_book_room({
        "guest_id": "gst_lucas",
        "guest_name": "Lucas Alencar",
        "guest_email": "lucas@viagens.com",
        "guest_document": "123.456.789-00",
        "room_number": "101",
        "check_in": "2026-10-12",   # Segunda
        "check_out": "2026-10-15",  # Quinta (3 noites x R$ 200 = R$ 600,00)
    })
    print(f"HTTP Status: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    res_id_1 = res.get("reservation_id")

    print("\n--- CENÁRIO 2: Reserva em Alta Temporada + Fim de Semana (Dezembro no Deluxe 201) ---")
    # Dezembro (+30%), Sexta e Sábado (+20%) calculados dinamicamente pelo Domain Service
    status, res = controller.handle_post_book_room({
        "guest_id": "gst_helena",
        "guest_name": "Helena Prado",
        "guest_email": "helena@luxo.com",
        "guest_document": "999.888.777-66",
        "room_number": "201",
        "check_in": "2026-12-18",   # Sexta-feira
        "check_out": "2026-12-21",  # Segunda-feira (3 noites)
    })
    print(f"HTTP Status: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    res_id_2 = res.get("reservation_id")

    print("\n--- CENÁRIO 3: Tentativa de Overbooking (Conflito de Datas no Quarto 101) ---")
    status, res = controller.handle_post_book_room({
        "guest_id": "gst_outro",
        "guest_name": "Marcos Conflito",
        "guest_email": "marcos@erro.com",
        "guest_document": "111.222.333-44",
        "room_number": "101",
        "check_in": "2026-10-14",   # Sobrepõe com a reserva de Lucas (12 a 15)
        "check_out": "2026-10-18",
    })
    print(f"HTTP Status: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 4: Cancelamento com Mais de 48h de Antecedência (Reembolso Integral de 100%) ---")
    # Cancelamento simulado em 08/10 para check-in em 12/10 (> 48h)
    cancel_time_early = datetime(2026, 10, 8, 10, 0, tzinfo=timezone.utc)
    status, res = controller.handle_post_cancel_reservation(res_id_1, cancel_time_early)
    print(f"HTTP Status: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 5: Nova Reserva e Cancelamento com 30h de Antecedência (Multa de 50%) ---")
    _, new_res = controller.handle_post_book_room({
        "guest_id": "gst_marcos",
        "guest_name": "Marcos Silveira",
        "guest_email": "marcos@silveira.com",
        "guest_document": "444.555.666-77",
        "room_number": "301",
        "check_in": "2026-11-10",
        "check_out": "2026-11-12",
    })
    res_id_3 = new_res.get("reservation_id")

    # Cancelado em 08/11 às 18h (30h antes do check-in de 10/11 00h)
    cancel_time_mid = datetime(2026, 11, 8, 18, 0, tzinfo=timezone.utc)
    status, res = controller.handle_post_cancel_reservation(res_id_3, cancel_time_mid)
    print(f"HTTP Status: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 6: Cancelamento com Menos de 24h / No-Show (Retenção de 100%) ---")
    # Cancelado em 18/12 às 10h para check-in de 18/12 (< 24h)
    cancel_time_late = datetime(2026, 12, 18, 10, 0, tzinfo=timezone.utc)
    status, res = controller.handle_post_cancel_reservation(res_id_2, cancel_time_late)
    print(f"HTTP Status: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 7: Falha de Pagamento na Casca Externa ---")
    status, res = controller.handle_post_book_room({
        "guest_id": "guest_declined",
        "guest_name": "Sem Saldo",
        "guest_email": "semsaldo@fail.com",
        "guest_document": "000.000.000-00",
        "room_number": "101",
        "check_in": "2026-11-01",
        "check_out": "2026-11-03",
    })
    print(f"HTTP Status: {status} | Resposta: {res}")

    print("\n" + "=" * 80)
    print(" Exemplo 01 de Onion Architecture finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
