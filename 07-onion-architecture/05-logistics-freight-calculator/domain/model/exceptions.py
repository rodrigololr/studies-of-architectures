"""Exceções do domínio logístico de cálculo de frete."""

class FreightDomainException(Exception):
    """Exceção base para regras de frete e transporte."""
    pass


class CargoOverweightException(FreightDomainException):
    """Lançada quando a carga excede a capacidade em peso do veículo."""
    pass


class VolumeExceededException(FreightDomainException):
    """Lançada quando o volume total da carga ultrapassa a capacidade cúbica da carroceria."""
    pass


class IncompatibleVehicleException(FreightDomainException):
    """Lançada quando o veículo não suporta o tipo de carga (ex: carga perigosa sem certificação)."""
    pass


class InvalidFreightOrderStateException(FreightDomainException):
    """Lançada em transições inválidas de estado do pedido de frete."""
    pass
