class DomainException(Exception):
    """Exceção base de violação de invariante de domínio."""
    pass

class AccountInactiveException(DomainException):
    """Lançada quando uma operação é tentada em conta não aberta ou encerrada."""
    pass

class InsufficientFundsException(DomainException):
    """Lançada quando uma tentativa de saque ou transferência excede o saldo disponível."""
    pass

class InvalidAmountException(DomainException):
    """Lançada quando valores monetários são menores ou iguais a zero."""
    pass

class AccountAlreadyExistsException(DomainException):
    """Lançada quando se tenta abrir uma conta com ID já existente."""
    pass

class ConcurrencyConflictException(Exception):
    """Lançada quando a versão esperada do stream não bate com a versão persistida."""
    pass
