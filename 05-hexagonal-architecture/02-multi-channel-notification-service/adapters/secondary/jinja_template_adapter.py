"""
jinja_template_adapter.py - Adaptador Secundário para renderização de templates.

Implementa `TemplateEnginePort` utilizando formatação parametrizada pura do Python,
sem exigir instalação externa do pacote jinja2.
"""

from __future__ import annotations
from typing import Dict, Any
from domain.exceptions import TemplateNotFoundException
from ports.driven import TemplateEnginePort


class SimpleTemplateEngineAdapter(TemplateEnginePort):
    def __init__(self) -> None:
        self._templates: Dict[str, str] = {
            "auth.2fa_token": "Olá {name}, seu código de segurança é {code}. Expira em {expires_minutes} minutos.",
            "order.confirmed": "Parabéns {name}! Seu pedido #{order_id} de R$ {total:.2f} foi aprovado com sucesso.",
            "security.alert": "Atenção {name}! Detectamos um login incomum a partir do IP {ip_address} em {location}.",
        }

    def register_template(self, name: str, template_str: str) -> None:
        self._templates[name] = template_str

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self._templates.get(template_name)
        if not template:
            raise TemplateNotFoundException(f"Template '{template_name}' não foi encontrado.")
        try:
            return template.format(**context)
        except KeyError as err:
            return template.format(**{**context, err.args[0]: f"<{err.args[0]}_MISSING>"})
