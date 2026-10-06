"""Parser e Serializador UN/EDIFACT D.01B DESADV (Despatch Advice)."""

from typing import List, Tuple
from canonical.supply_chain_models import (
    DespatchLineItem,
    CanonicalDespatchAdvice,
)


class EdifactSyntaxError(ValueError):
    """Erro de sintaxe ou integridade de segmentos EDIFACT."""
    pass


class EdifactDesadvParser:
    """Parser para mensagens logísticas UN/EDIFACT DESADV."""

    @staticmethod
    def parse(edifact_content: str) -> CanonicalDespatchAdvice:
        # Divide por terminador de segmento padrão "'"
        raw_segments = [s.strip() for s in edifact_content.split("'") if s.strip()]
        if not raw_segments:
            raise EdifactSyntaxError("Mensagem EDIFACT vazia.")

        # Validação do trailer UNT
        last_seg = raw_segments[-1]
        if not last_seg.startswith("UNT+"):
            raise EdifactSyntaxError("Segmento de encerramento UNT não encontrado.")

        unt_parts = last_seg.split("+")
        if len(unt_parts) < 3:
            raise EdifactSyntaxError("Segmento UNT mal formatado.")

        expected_count = int(unt_parts[1])
        actual_count = len(raw_segments)
        if expected_count != actual_count:
            raise EdifactSyntaxError(
                f"Contagem de segmentos inválida no UNT: esperado {expected_count}, encontrado {actual_count}."
            )

        doc_id = ""
        despatch_date = ""
        buyer_code = ""
        supplier_code = ""
        items: List[DespatchLineItem] = []

        current_line_num = 0
        current_part = ""

        for seg in raw_segments:
            parts = seg.split("+")
            tag = parts[0]

            if tag == "BGM":
                # BGM+351+DN-88491+9
                doc_id = parts[2]
            elif tag == "DTM":
                # DTM+137:20261006:102
                date_subparts = parts[1].split(":")
                despatch_date = date_subparts[1]
            elif tag == "NAD":
                # NAD+BY+OEM-VOLKSWAGEN ou NAD+SE+BOSCH-BRAZIL
                role = parts[1]
                code = parts[2]
                if role == "BY":
                    buyer_code = code
                elif role == "SE":
                    supplier_code = code
            elif tag == "LIN":
                # LIN+1++PART-INJ-009:IN
                current_line_num = int(parts[1])
                subparts = parts[3].split(":")
                current_part = subparts[0]
            elif tag == "QTY":
                # QTY+12:450:PCE
                qty_subparts = parts[1].split(":")
                qty = int(qty_subparts[1])
                uom = qty_subparts[2] if len(qty_subparts) > 2 else "PCE"
                items.append(
                    DespatchLineItem(
                        line_number=current_line_num,
                        part_number=current_part,
                        description=f"Auto Component {current_part}",
                        quantity=qty,
                        unit_of_measure=uom,
                    )
                )

        if not doc_id:
            raise EdifactSyntaxError("Segmento BGM obrigatório ausente.")

        return CanonicalDespatchAdvice(
            document_id=doc_id,
            despatch_date=despatch_date,
            buyer_code=buyer_code,
            supplier_code=supplier_code,
            items=items,
        )

    @staticmethod
    def generate_acknowledgement(doc_id: str, is_accepted: bool, error_msg: str = "") -> str:
        """Gera resposta EDIFACT CONTRL / APERAK."""
        code = "7" if is_accepted else "27"  # 7 = Aprovado, 27 = Rejeitado
        return (
            f"UNH+1+CONTRL:2:1:UN'"
            f"UCI+{doc_id}+{code}'"
            f"{f'FTX+AAI+++{error_msg[:70]}\'' if error_msg else ''}"
            f"UNT+4+1'"
        )
