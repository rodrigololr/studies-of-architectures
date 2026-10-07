class CartException(Exception):
    """Exceção base de regras do carrinho."""
    pass

class CartInactiveException(CartException):
    """Lançada quando se tenta operar em um carrinho já finalizado ou abandonado."""
    pass

class EmptyCartException(CartException):
    """Lançada quando se tenta checkout em carrinho sem itens."""
    pass

class ProductNotFoundInCartException(CartException):
    """Lançada ao tentar alterar ou remover produto ausente no carrinho."""
    pass

class InvalidCartOperationException(CartException):
    """Lançada ao violar regras de quantidade ou cupom."""
    pass

class ConcurrencyConflictException(Exception):
    """Lançada ao ocorrer colisão de versão no stream do carrinho."""
    pass
