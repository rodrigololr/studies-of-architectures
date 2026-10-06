"""Item de Carga e propriedades físicas (Value Object)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CargoItem:
    """Item de carga a ser transportado (Value Object)."""
    description: str
    weight_kg: float
    length_m: float  # Comprimento
    width_m: float   # Largura
    height_m: float  # Altura
    declared_value: float  # Valor declarado da mercadoria para cálculo de seguro/GRIS
    is_hazardous: bool = False  # Carga perigosa (ex: químicos, inflamáveis)
    is_fragile: bool = False    # Carga frágil (ex: vidros, eletrônicos)

    @property
    def volume_m3(self) -> float:
        """Volume cúbico do item."""
        return round(self.length_m * self.width_m * self.height_m, 4)
