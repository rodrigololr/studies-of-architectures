"""Adaptador de infraestrutura para cálculo de pedágios por rota (Ring 4)."""

from domain.model.vehicle_capacity import TruckType
from application.interfaces import ITollRateApiGateway


class MockNationalTollApiGateway(ITollRateApiGateway):
    """Simulador de integração com API de pedágios (ex: Sem Parar / CCR / ANTT)."""
    
    # Tarifa média estimada por praça de pedágio por tipo de caminhão
    TOLL_AXLE_MULTIPLIER = {
        TruckType.VUC: 14.50,
        TruckType.TOCO: 29.00,
        TruckType.TRUCK: 43.50,
        TruckType.CARRETA: 72.50,
    }

    # Praças estimadas nas rotas mapeadas
    ROUTE_TOLL_BOOTHS = {
        ("SAO PAULO", "CURITIBA"): 5,
        ("SAO PAULO", "RIO DE JANEIRO"): 4,
        ("SAO PAULO", "SALVADOR"): 14,
        ("CURITIBA", "PORTO ALEGRE"): 7,
    }

    def calculate_tolls(self, origin: str, destination: str, truck_type: TruckType) -> float:
        route_key = (origin.strip().upper(), destination.strip().upper())
        # Tenta a rota direta ou reversa, ou assume 1 praça a cada 100km
        booths = self.ROUTE_TOLL_BOOTHS.get(
            route_key,
            self.ROUTE_TOLL_BOOTHS.get((route_key[1], route_key[0]), 3)
        )
        base_rate = self.TOLL_AXLE_MULTIPLIER.get(truck_type, 30.0)
        return round(booths * base_rate, 2)
