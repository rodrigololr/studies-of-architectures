"""Catalog Microservice - Responsável exclusivo pelos dados descritivos de produtos."""

from typing import Dict, Any, Optional, List


class CatalogService:
    """Microsserviço de Catálogo com banco de dados próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._db: Dict[str, Dict[str, Any]] = {
            "PROD-001": {
                "id": "PROD-001",
                "title": "Smartphone Galaxy S24 Ultra",
                "short_description": "Smartphone premium com IA integrada e câmera de 200MP.",
                "full_description": "O Galaxy S24 Ultra é o smartphone definitivo da Samsung, com estrutura em titânio, tela Dynamic AMOLED 2X de 6.8 polegadas, processador Snapdragon 8 Gen 3 for Galaxy, e caneta S Pen integrada.",
                "category": "Eletrônicos > Celulares",
                "brand": "Samsung",
                "specs": {
                    "Tela": "6.8 polegadas QHD+",
                    "Processador": "Snapdragon 8 Gen 3",
                    "Memoria_RAM": "12GB",
                    "Armazenamento": "512GB",
                    "Bateria": "5000 mAh",
                },
                "images": [
                    "https://cdn.store.com/s24u-front.jpg",
                    "https://cdn.store.com/s24u-back.jpg",
                    "https://cdn.store.com/s24u-angle.jpg",
                ],
            },
            "PROD-002": {
                "id": "PROD-002",
                "title": "Notebook Dell XPS 14",
                "short_description": "Ultrabook compacto com tela OLED 3.2K e Intel Core Ultra 7.",
                "full_description": "Notebook ultrafino de alta performance Dell XPS 14 com chassis em alumínio usinado CNC, tela sensível ao toque OLED 3.2K e GPU NVIDIA RTX 4050.",
                "category": "Informática > Laptops",
                "brand": "Dell",
                "specs": {
                    "Processador": "Intel Core Ultra 7 155H",
                    "Memoria_RAM": "32GB LPDDR5x",
                    "Armazenamento": "1TB NVMe SSD",
                    "GPU": "NVIDIA GeForce RTX 4050 6GB",
                },
                "images": [
                    "https://cdn.store.com/xps14-open.jpg",
                    "https://cdn.store.com/xps14-closed.jpg",
                ],
            },
        }

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(product_id)
