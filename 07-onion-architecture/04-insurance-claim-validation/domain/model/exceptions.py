"""Exceções do domínio de regulação e validação de sinistros."""

class InsuranceDomainException(Exception):
    """Exceção base do domínio de seguros."""
    pass


class PolicyExpiredException(InsuranceDomainException):
    """Lançada quando o sinistro ocorre fora da vigência da apólice."""
    pass


class PolicySuspendedException(InsuranceDomainException):
    """Lançada quando a apólice está inadimplente ou suspensa."""
    pass


class InvalidClaimStateException(InsuranceDomainException):
    """Lançada quando uma transição inválida de estado do sinistro é solicitada."""
    pass


class CoverageExcludedException(InsuranceDomainException):
    """Lançada quando a causa do sinistro está na lista de exclusões expressas."""
    pass
