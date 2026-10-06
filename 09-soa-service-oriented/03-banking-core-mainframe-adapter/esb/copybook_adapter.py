"""Adaptador COBOL Copybook: Serialização e Desserialização de Buffers Posicionais."""

from canonical.banking_models import (
    CanonicalTransactionRequest,
    CanonicalTransactionResponse,
)


class MainframeCopybookAdapter:
    """Componente do ESB responsável pela serialização/desserialização do layout de mainframe."""

    @staticmethod
    def encode_request(req: CanonicalTransactionRequest) -> str:
        """Codifica o modelo canônico em um buffer posicional de exatamente 33 caracteres.
        
        Layout COBOL COPYBOOK de Entrada (33 bytes):
        - 00-09: TX-ID (PIC X(10))
        - 10-13: AGENCIA (PIC 9(4))
        - 14-20: CONTA (PIC 9(7))
        - 21-31: VALOR-CENTAVOS (PIC 9(11))
        - 32-32: TIPO-TRANSACAO (PIC X(1) - 'D' ou 'C')
        """
        tx_id_field = f"{req.transaction_id[:10]:<10}"
        branch_field = f"{int(req.account.branch_code):04d}"
        account_field = f"{int(req.account.account_number):07d}"
        
        # Converte float para centavos inteiros (ex: 150.50 -> 15050)
        centavos = int(round(req.amount_brl * 100))
        valor_field = f"{centavos:011d}"
        
        tipo_field = req.transaction_type.upper()[:1]

        buffer = f"{tx_id_field}{branch_field}{account_field}{valor_field}{tipo_field}"
        assert len(buffer) == 33, f"Buffer Copybook deve ter exatamente 33 caracteres (tem {len(buffer)})"
        return buffer

    @staticmethod
    def decode_response(tx_id: str, buffer_out: str) -> CanonicalTransactionResponse:
        """Decodifica o buffer de 39 caracteres retornado pelo Mainframe IBM z/OS CICS.
        
        Layout de Saída:
        - 00-09: TX-ID (PIC X(10))
        - 10-11: RETURN-CODE (PIC 9(2))
        - 12-22: NOVO-SALDO-CENTAVOS (PIC 9(11))
        - 23-38: AUTH-STAMP (PIC X(16))
        """
        ret_code = buffer_out[10:12]
        saldo_centavos = int(buffer_out[12:23])
        novo_saldo_brl = round(saldo_centavos / 100.0, 2)
        auth_stamp = buffer_out[23:39].strip()

        if ret_code == "00":
            return CanonicalTransactionResponse(
                transaction_id=tx_id,
                is_success=True,
                return_code="00",
                new_balance_brl=novo_saldo_brl,
                auth_stamp=auth_stamp,
                message="Transação contábil liquidada com sucesso no Mainframe.",
            )
        elif ret_code == "51":
            return CanonicalTransactionResponse(
                transaction_id=tx_id,
                is_success=False,
                return_code="51",
                new_balance_brl=novo_saldo_brl,
                auth_stamp="",
                message="Transação recusada: Saldo contábil insuficiente na conta corrente.",
            )
        elif ret_code == "14":
            return CanonicalTransactionResponse(
                transaction_id=tx_id,
                is_success=False,
                return_code="14",
                new_balance_brl=0.0,
                auth_stamp="",
                message="Transação recusada: Conta corrente ou agência não localizada no ledger.",
            )
        else:
            return CanonicalTransactionResponse(
                transaction_id=tx_id,
                is_success=False,
                return_code=ret_code,
                new_balance_brl=0.0,
                auth_stamp="",
                message=f"Erro de processamento no Core Mainframe (Código: {ret_code}).",
            )
