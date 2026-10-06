"""Provedor Porto Seguro: Serviço Legado SOAP / XML."""

import uuid
import xml.etree.ElementTree as ET


class PortoSeguroSoapService:
    """Simulador de Web Service SOAP da Porto Seguro.
    
    Espera envelope XML com tags específicas e retorna XML.
    """

    def quote_policy_soap(self, xml_payload: str) -> str:
        try:
            root = ET.fromstring(xml_payload)
            ano = int(root.findtext(".//VeiculoAno", "2020"))
            valor_fipe = float(root.findtext(".//ValorFipe", "0.0"))
            idade_condutor = int(root.findtext(".//CondutorIdade", "30"))
            tipo_cobertura = root.findtext(".//TipoCobertura", "STANDARD")
            tem_garagem = root.findtext(".//PossuiGaragem", "false").lower() == "true"
        except Exception as exc:
            return f"<PortoResponse><Status>ERRO_SCHEMA</Status><Mensagem>{exc}</Mensagem></PortoResponse>"

        # Regra de Subscrição da Porto: Condutores abaixo de 21 anos são recusados
        if idade_condutor < 21:
            return (
                f"<PortoResponse>"
                f"<Status>RECUSADO</Status>"
                f"<Motivo>Perfil de risco nao aceito: Condutor com idade inferior a 21 anos</Motivo>"
                f"</PortoResponse>"
            )

        # Cálculo de Prêmio
        taxa = 0.045
        if tipo_cobertura == "BASIC":
            taxa = 0.030
        elif tipo_cobertura == "COMPREHENSIVE":
            taxa = 0.058

        if tem_garagem:
            taxa *= 0.90  # 10% de desconto por pernoite em garagem

        premio = round(valor_fipe * taxa, 2)
        franquia = round(valor_fipe * 0.048, 2)
        protocolo = f"PORTO-{uuid.uuid4().hex[:8].upper()}"

        return (
            f"<PortoResponse>"
            f"<Status>APROVADO</Status>"
            f"<Protocolo>{protocolo}</Protocolo>"
            f"<PremioAnual>{premio:.2f}</PremioAnual>"
            f"<Franquia>{franquia:.2f}</Franquia>"
            f"<Cobertura>{tipo_cobertura}</Cobertura>"
            f"</PortoResponse>"
        )
