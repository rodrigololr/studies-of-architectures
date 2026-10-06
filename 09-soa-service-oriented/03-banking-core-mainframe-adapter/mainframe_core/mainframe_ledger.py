"""Simulador de Core Bancário Mainframe IBM z/OS CICS em COBOL.

Opera estritamente via buffers de tamanho fixo posicionais (COBOL Copybooks).
Não compreende JSON, XML ou tipos dinâmicos.
"""

from typing import Dict


class MainframeCobolCore:
    """Core bancário contábil legado."""
    def __init__(self) -> None:
        # Ledger de contas no Mainframe: "(agencia, conta)" -> saldo_em_centavos (int)
        self._ledger: Dict[str, int] = {
            "0142_0099120": 500_000,  # R$ 5.000,00 (500.000 centavos)
            "0142_0088340": 120_000,  # R$ 1.200,00
        }

    def process_copybook_transaction(self, fixed_buffer_in: str) -> str:
        """Processa buffer fixo de 33 caracteres de entrada e retorna 39 caracteres de saída."""
        if len(fixed_buffer_in) != 33:
            return f"{fixed_buffer_in[:10]:<10}9900000000000ERR_BAD_PAYLOAD "

        tx_id = fixed_buffer_in[0:10].strip()
        agencia = fixed_buffer_in[10:14]
        conta = fixed_buffer_in[14:21]
        valor_str = fixed_buffer_in[21:32]
        tipo = fixed_buffer_in[32:33]

        account_key = f"{agencia}_{conta}"
        if account_key not in self._ledger:
            # Código 14: Conta inexistente
            return f"{tx_id:<10}1400000000000NO_ACCOUNT_FOUND"

        valor_centavos = int(valor_str)
        saldo_atual = self._ledger[account_key]

        if tipo == "D":
            if saldo_atual < valor_centavos:
                # Código 51: Saldo insuficiente
                saldo_str = f"{saldo_atual:011d}"
                return f"{tx_id:<10}51{saldo_str}INSUFFICIENT_FND"
            saldo_atual -= valor_centavos
        elif tipo == "C":
            saldo_atual += valor_centavos
        else:
            return f"{tx_id:<10}9800000000000INVALID_TX_TYPE "

        self._ledger[account_key] = saldo_atual
        novo_saldo_str = f"{saldo_atual:011d}"
        auth_stamp = f"CICS_{tx_id[:8]:<11}"

        # Código 00: Sucesso contábil absoluto
        return f"{tx_id:<10}00{novo_saldo_str}{auth_stamp}"
