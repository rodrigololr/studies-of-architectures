"""Serviço de Inventário de SIM Cards e Numeração."""

from typing import Set, Dict


class SimCardInventoryService:
    def __init__(self) -> None:
        # Estoque de chips válidos e disponíveis
        self._available_iccids: Set[str] = set()
        self._allocated_iccids: Dict[str, str] = {}  # iccid -> msisdn

    def add_sim_to_warehouse(self, iccid: str) -> None:
        self._available_iccids.add(iccid)

    def validate_and_allocate(self, iccid: str, msisdn: str) -> bool:
        if iccid not in self._available_iccids:
            return False
        self._available_iccids.remove(iccid)
        self._allocated_iccids[iccid] = msisdn
        return True

    def release_sim(self, iccid: str) -> None:
        if iccid in self._allocated_iccids:
            del self._allocated_iccids[iccid]
            self._available_iccids.add(iccid)
