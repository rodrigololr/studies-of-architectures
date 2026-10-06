"""API Gateway: Ponto único de entrada, roteamento reverso e segurança."""

import json
from dataclasses import dataclass
from typing import Dict, Any, Optional
from gateway.mobile_bff import MobileBff
from gateway.web_desktop_bff import WebDesktopBff


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    headers: Dict[str, str]
    body: Dict[str, Any]
    payload_size_bytes: int


class ApiGateway:
    """API Gateway corporativo mascarando a topologia interna de microsserviços."""

    def __init__(self, mobile_bff: MobileBff, web_bff: WebDesktopBff) -> None:
        self._mobile_bff = mobile_bff
        self._web_bff = web_bff
        self._valid_tokens = {"token-mobile-secret-xyz", "token-web-secret-abc"}

    def handle_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
    ) -> GatewayResponse:
        # 1. Autenticação e Segurança no Gateway
        auth_header = headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        if token not in self._valid_tokens:
            body = {"error": "Unauthorized", "message": "Token de autenticação ausente ou inválido."}
            payload_str = json.dumps(body)
            return GatewayResponse(
                status_code=401,
                headers={"Content-Type": "application/json"},
                body=body,
                payload_size_bytes=len(payload_str.encode("utf-8")),
            )

        # 2. Roteamento Reverso para BFF Mobile
        if path.startswith("/api/v1/mobile/products/"):
            product_id = path.split("/")[-1]
            data = self._mobile_bff.get_mobile_product_details(product_id)
            if not data:
                return self._not_found_response("Produto não localizado no catálogo.")
            return self._success_response(data)

        # 3. Roteamento Reverso para BFF Web
        elif path.startswith("/api/v1/web/products/"):
            product_id = path.split("/")[-1]
            data = self._web_bff.get_web_product_details(product_id)
            if not data:
                return self._not_found_response("Produto não localizado no catálogo.")
            return self._success_response(data)

        # 4. Rota Inexistente
        return self._not_found_response("Endpoint não roteável no API Gateway.")

    def _success_response(self, body: Dict[str, Any]) -> GatewayResponse:
        payload_str = json.dumps(body)
        return GatewayResponse(
            status_code=200,
            headers={"Content-Type": "application/json", "X-Gateway-Route": "Microservices-BFF"},
            body=body,
            payload_size_bytes=len(payload_str.encode("utf-8")),
        )

    def _not_found_response(self, msg: str) -> GatewayResponse:
        body = {"error": "Not Found", "message": msg}
        payload_str = json.dumps(body)
        return GatewayResponse(
            status_code=404,
            headers={"Content-Type": "application/json"},
            body=body,
            payload_size_bytes=len(payload_str.encode("utf-8")),
        )
