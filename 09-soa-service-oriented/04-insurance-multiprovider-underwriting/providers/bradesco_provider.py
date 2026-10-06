"""Provedor Bradesco Seguros: Serviço Legado RPC com Strings Delimitadas."""

import uuid


class BradescoRpcService:
    """Simulador de Serviço Legado Bradesco Seguros via Socket/RPC delimitado por pipe '|'."""

    def quote_policy_rpc(self, pipe_string: str) -> str:
        fields = {}
        for part in pipe_string.split("|"):
            if ":" in part:
                k, v = part.split(":", 1)
                fields[k.strip().upper()] = v.strip()

        valor_fipe = float(fields.get("VALOR", "0.0"))
        cobertura = fields.get("COBERTURA", "STANDARD")

        # Regra de Subscrição Bradesco: Veículos acima de R$ 300.000 exigem auditoria presencial
        if valor_fipe > 300000.0:
            return "STATUS:RECUSADO|MOTIVO:VALOR_EXCEDE_LIMITE_AUTOMATICO_300K"

        taxa = 0.042
        if cobertura == "BASIC":
            taxa = 0.029
        elif cobertura == "COMPREHENSIVE":
            taxa = 0.055

        premio = round(valor_fipe * taxa, 2)
        franquia = round(valor_fipe * 0.040, 2)
        protocolo = f"BRAD-{uuid.uuid4().hex[:8].upper()}"

        return f"STATUS:APROVADO|PROTOCOLO:{protocolo}|PREMIO:{premio:.2f}|FRANQUIA:{franquia:.2f}|COBERTURA:{cobertura}"
